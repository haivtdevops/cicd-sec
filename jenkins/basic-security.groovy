import jenkins.model.*
import hudson.security.*

def instance = Jenkins.getInstance()

// Tạo realm với user nội bộ
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount("admin", "@dmin@123!")
instance.setSecurityRealm(hudsonRealm)

// Chỉ cho phép user login mới có quyền, không cho anonymous
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.save()

