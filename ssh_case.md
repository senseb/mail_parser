Problem: 

ssh xxx ＝> Permission denied (publickey,keyboard-interactive).
> step 1: chmod 700 ~/.ssh
> step 2: chmod 600 ~/.ssh/config
> step 3: chown $USER ~/.ssh/config

see: https://serverfault.com/questions/253313/ssh-returns-bad-owner-or-permissions-on-ssh-config for detail
