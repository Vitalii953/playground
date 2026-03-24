# async def loop(player: Player, language: languages, redis: Redis):
#     """
#     this is the main loop of the game, it is called by the main function
#     it is responsible for calling go_one_step and handling its result
#     """
#     # initialize player
#     ...


#     while player.is_alive():
#         result = await go_one_step(player, language, redis)
#         # handle result if needed (e.g. if it has 'needs_input' then store it in state and wait for frontend input)


#     # player is dead
#     player.die(timer)

#     # TODO: create timer, create player if doesn't exist, work with db for state of player (equipment, money etc...)
