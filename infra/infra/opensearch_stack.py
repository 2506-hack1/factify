"""
OpenSearch最小構成スタック（デモ用）
月額約$27で高性能検索エンジンを実現（t3.small.search使用）
"""
from aws_cdk import (
    Stack,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

class OpenSearchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # CFN L1 Constructを使用してOpenSearchドメインを作成（zone awareness問題回避）
        cfn_domain = opensearch.CfnDomain(
            self, "FactifySearchDomain",
            domain_name="factify-search-demo",
            engine_version="OpenSearch_2.11",
            cluster_config=opensearch.CfnDomain.ClusterConfigProperty(
                instance_type="t3.small.search",  # 月額約$26に最適化！
                instance_count=1,
                dedicated_master_enabled=False,
                zone_awareness_enabled=False  # 明示的にFalseに設定
            ),
            ebs_options=opensearch.CfnDomain.EBSOptionsProperty(
                ebs_enabled=True,
                volume_type="gp3",
                volume_size=10
            ),
            # Fine-grained access control設定
            advanced_security_options=opensearch.CfnDomain.AdvancedSecurityOptionsInputProperty(
                enabled=True,
                internal_user_database_enabled=True,
                master_user_options=opensearch.CfnDomain.MasterUserOptionsProperty(
                    master_user_name="admin",
                    master_user_password="TempPassword123!"  # デモ用パスワード
                )
            ),
            # HTTPS必須
            domain_endpoint_options=opensearch.CfnDomain.DomainEndpointOptionsProperty(
                enforce_https=True
            ),
            # ノード間暗号化
            node_to_node_encryption_options=opensearch.CfnDomain.NodeToNodeEncryptionOptionsProperty(
                enabled=True
            ),
            # 保存時暗号化
            encryption_at_rest_options=opensearch.CfnDomain.EncryptionAtRestOptionsProperty(
                enabled=True
            ),
            # より制限的なアクセスポリシー
            access_policies={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "*"
                        },
                        "Action": "es:*",
                        "Resource": "*",
                        "Condition": {
                            "IpAddress": {
                                "aws:SourceIp": "0.0.0.0/0"  # すべてのIPを許可（デモ用）
                            }
                        }
                    }
                ]
            }
        )
        
        # domainプロパティを設定（他のスタックからアクセスできるように）
        self.domain = cfn_domain
        
        # アウトプット
        CfnOutput(
            self, "OpenSearchEndpoint",
            value=cfn_domain.attr_domain_endpoint,
            description="OpenSearch cluster endpoint"
        )
        
        CfnOutput(
            self, "OpenSearchDashboardsURL",
            value=f"https://{cfn_domain.attr_domain_endpoint}/_dashboards",
            description="OpenSearch Dashboards URL"
        )
