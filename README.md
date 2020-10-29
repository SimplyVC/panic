# Errors when running on different machine

Running command `docker-compose up -d --build`
Error received: `Creating network "panic_panic_net" with the default driver ERROR: Pool overlaps with other one on this address space`
Solution: `docker network prune`

# Changing durability of rabbitmq exchange

When changing durability of rabbitmq exchange from `True` to `False` or vice-versa you must delete the exchange in rabbitmq

Solution:
If you are running rabbitmq in docker then run this command, replace `DOCKER_ID` with the docker id found corresponding to rabbitmq container when running
`docker ps`. You will also need to provide the name of the exchange that you are changing the durability of in `EXHCNAGE_NAME`. Command : `docker exec -it DOCKER_CONTAINER_ID rabbitmqadmin delete exchange name='EXCHANGE_NAME'`.
