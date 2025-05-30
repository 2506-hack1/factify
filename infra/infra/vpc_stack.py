from aws_cdk import (
    aws_ec2 as ec2,
    core,
)

class FastApiVpcStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. VPCの作成
        # max_azs: デプロイするアベイラビリティゾーンの最大数
        # nat_gateways: NATゲートウェイの数
        # cidr: VPCのCIDRブロック
        self.vpc = ec2.Vpc(
            self, "FastApiVpc",
            max_azs=1,
            nat_gateways=1,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24
                ),
            ]
        )

        # VPCのIDやサブネットIDをOutputsとして出力しておくと、AWSマネジメントコンソールや
        # 別のスタックから参照する際に便利です。
        core.CfnOutput(self, "VpcId", value=self.vpc.vpc_id, description="ID of the created VPC")
        core.CfnOutput(self, "PublicSubnets",
                       value=",".join([s.subnet_id for s in self.vpc.public_subnets]),
                       description="Comma-separated list of Public Subnet IDs")
        core.CfnOutput(self, "PrivateSubnets",
                       value=",".join([s.subnet_id for s in self.vpc.private_subnets]),
                       description="Comma-separated list of Private Subnet IDs")
