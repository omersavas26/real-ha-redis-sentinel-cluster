yum update
yum -y install keepalived

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "net.ipv4.ip_nonlocal_bind=1" >> /etc/sysctl.conf
sysctl -p


mv /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.org
cp keepalived.conf /etc/keepalived/keepalived.conf

chmod 644 /etc/keepalived/keepalived.conf

systemctl start keepalived
systemctl enable keepalived