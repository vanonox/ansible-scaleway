DOCKER_DNS_IP=$(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' powerdns_master)

all: clean build_docker

docker_dns_ip:
	@echo ${DOCKER_DNS_IP}

build_docker:
	@docker build -f Dockerfile-python2 -t scaleway/ansible_domain_test:python2 .
	@docker build -f Dockerfile-python3 -t scaleway/ansible_domain_test:python3 .

clean:
	- @docker rmi scaleway/ansible_domain_test:python2
	- @docker rmi scaleway/ansible_domain_test:python3

tests_dns_python2:
	docker run -it --rm --volume `pwd`:/app --network host scaleway/ansible_domain_test:python2 ansible-playbook --connection=local -i vars_example play_test_dns*.yml

tests_domain_python2:
	docker run -it --rm --volume `pwd`:/app --network host scaleway/ansible_domain_test:python2 ansible-playbook --connection=local -i vars_example play_test_domain*.yml

tests_all_python2: tests_dns_python2 tests_domain_python2

shell_python2:
	- @echo "ansible-playbook --connection=local -i vars_example play_testxxxx.yml"
	@docker run -it --rm --volume `pwd`:/app --network host scaleway/ansible_domain_test:python2 sh

tests_dns_python3:
	docker run -it --rm --volume `pwd`:/app --network host scaleway/ansible_domain_test:python3 ansible-playbook --connection=local -e 'ansible_python_interpreter=/usr/bin/python3' -i vars_example play_test_dns*.yml

tests_domain_python3:
	docker run -it --rm --volume `pwd`:/app --network host scaleway/ansible_domain_test:python3 ansible-playbook --connection=local -e 'ansible_python_interpreter=/usr/bin/python3' -i vars_example play_test_domain*.yml

tests_all_python3: tests_dns_python3 tests_domain_python3

shell_python3:
	- @echo "ansible-playbook --connection=local -e 'ansible_python_interpreter=/usr/bin/python3' -i vars_example play_testxxxx.yml"
	@docker run -it --rm --volume `pwd`:/app --network host  -e 'ansible_python_interpreter=/usr/bin/python3' scaleway/ansible_domain_test:python3 sh
