# infra/lib/vpc_stack.py
from aws_cdk import (
    aws_ec2 as ec2,
    App, Stack, CfnOutput
)

# class FastApiVpcStack(core.Stack): # 修正前
class FastApiVpcStack(Stack): # 修正後
    def __init__(self, scope: App, id: str, **kwargs) -> None: # scopeの型ヒントもAppに
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(
            self, "FastApiVpc",
            max_azs=2,
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

        # core.CfnOutput(self, "VpcId", value=self.vpc.vpc_id, description="ID of the created VPC") # 修正前
        CfnOutput(self, "VpcId", value=self.vpc.vpc_id, description="ID of the created VPC") # 修正後
        CfnOutput(self, "PublicSubnets",
                       value=",".join([s.subnet_id for s in self.vpc.public_subnets]),
                       description="Comma-separated list of Public Subnet IDs")
        CfnOutput(self, "PrivateSubnets",
                       value=",".join([s.subnet_id for s in self.vpc.private_subnets]),
                       description="Comma-separated list of Private Subnet IDs")
