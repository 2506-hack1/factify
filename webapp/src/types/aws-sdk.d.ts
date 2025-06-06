// AWS SDK型定義の補完
declare module '@aws-sdk/client-cognito-identity-provider' {
  export class CognitoIdentityProviderClient {
    constructor(config: any);
    send(command: any): Promise<any>;
  }
  
  export class SignUpCommand {
    constructor(params: any);
  }
  
  export class ConfirmSignUpCommand {
    constructor(params: any);
  }
  
  export class InitiateAuthCommand {
    constructor(params: any);
  }
  
  export class GetUserCommand {
    constructor(params: any);
  }
  
  export class GlobalSignOutCommand {
    constructor(params: any);
  }
}
