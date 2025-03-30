tar cvf - looking-glass-client-B7.0.0 | pigz -9 -p 32 > looking-glass-client-B7.0.0.tar.gz

rpmbuild -bs path-to.spec
mock -r fedora-41-x86_64 /home/user/rpmbuild/SRPMS/path-to.src.rpm