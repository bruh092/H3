def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
@client.command(name="eval")
@is_owner()
async def eval_fn(ctx, *, cmd):
    try:
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'client': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        embed=discord.Embed(title="Eval success", description=f"py\n```{result}```",color = discord.Color(0x00ff6a),case_insensitive=True)
        embed.set_footer(text=f"execute time\n{client.latency} ms")
        await ctx.send(embed=embed)
        channel = client.get_channel(850591116554141706)

        embed2 = discord.Embed(title="Eval log", colour=discord.Colour.green())
        embed2.add_field(name="Input", value=f"```py\n{cmd}```", inline=False)
        embed2.add_field(name="Result", value=f"```py\n{result}```", inline=False)


        await channel.send(embed=embed2)

    except BaseException as error:
        em = discord.Embed(title="Eval false",description=f'```{error}```',color= discord.Color.orange())
        await ctx.send(embed=em)
