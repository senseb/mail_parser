
> ssh xxx ＝> Permission denied (publickey,keyboard-interactive).
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chown $USER ~/.ssh/config

see: https://serverfault.com/questions/253313/ssh-returns-bad-owner-or-permissions-on-ssh-config for detail
