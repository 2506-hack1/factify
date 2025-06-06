from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct


class S3CloudFrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, api_endpoint: str = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for hosting static website
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=f"factify-webapp-{self.account}-{self.region}",
            public_read_access=False,  # CloudFront経由でのみアクセス
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,  # 開発環境用
            auto_delete_objects=True,  # 開発環境用
        )

        # CloudFront Distribution with modern S3 origin (CDK v2)
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                # SPAのため、すべての404を index.html にリダイレクト
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=None,
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=None,
                ),
            ],
        )

        # S3Origin automatically sets up the necessary permissions for CloudFront access
        # No manual OAI grant needed with the simplified S3Origin approach


        # Environment variables for build
        environment_variables = {}
        if api_endpoint:
            environment_variables["VITE_API_ENDPOINT"] = api_endpoint

        # Outputs
        CfnOutput(
            self,
            "WebsiteBucketName",
            value=website_bucket.bucket_name,
            description="S3 Bucket Name"
        )

        CfnOutput(
            self,
            "WebsiteURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="Website URL"
        )

        CfnOutput(
            self,
            "CloudFrontDistributionId",
            value=distribution.distribution_id,
            description="CloudFront Distribution ID"
        )

        # Store for other stacks
        self.website_bucket = website_bucket
        self.distribution = distribution
        self.website_url = f"https://{distribution.distribution_domain_name}"
