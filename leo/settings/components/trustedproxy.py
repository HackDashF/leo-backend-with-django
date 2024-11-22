# this is added to allow a trusted proxy (ec2 load balancer) to terminate ssl and send http traffic
# when using this, incoming traffic must be restricted to the trusted proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
