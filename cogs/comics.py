#!/bin/env python

import discord
import json
from discord.ext import commands
from utils import dict_manip as dm
import xkcd as xklib

"""
This whole thing is a doozy.
The xkcd_blob.json file was generated by using a td-idf algorithm from Natural Language Toolkit (nltk).
I grabbed the 10 most important words from an xkcd's title and alt-text and transcript (if available).
The functions below try to find whole-word matches to this list in the xkcd_blob.json file.
It will return the comic with the most whole-word matches.
"""


class Comics:
    def __init__(self, bot):
        self.bot = bot

    def sync_get_xkcd(word_list=None) -> dict:
        """ Non a-sync function utilizing xkcd library """

        # Short circuit upon no alpha input --> rand comic
        if not word_list:
            comic_obj = xklib.getRandomComic()
            return {'title': comic_obj.getTitle(), 'image_link': comic_obj.getImageLink(), 'random': True, 'hits': 0}

        # pre-generated blob file
        with open('data/xkcd_blob.json') as f:
            json_blob_data = json.load(f)

        # Remove nonalpha phrases
        for x in word_list[:]:
            if not x.isalpha():
                word_list.remove(x)

        # Store the keys of matching comics as well as how many hits we got on each
        match_dict = {}
        for key, value in json_blob_data.items():
            count = 0
            for uw in word_list:
                if uw in json_blob_data[key]['tfidf_words']:
                    count += 1

            match_dict[json_blob_data[key]['num']] = count

        # Get comic with max number of hits
        n = dm.key_with_max_value(match_dict)

        # Max hits == 0 --> random comic
        if not match_dict[n]:
            comic_obj = xklib.getRandomComic()
            return {'title': comic_obj.getTitle(), 'image_link': comic_obj.getImageLink(), 'random': True, 'hits': 0}

        else:  # It actually worked? Nice
            comic_obj = xklib.getComic(n)
            return {'title': comic_obj.getTitle(), 'image_link': comic_obj.getImageLink(), 'random': False, 'hits': match_dict[n]}

    @commands.command(name='xkcd', aliases=['xk', 'x'])
    async def get_xkcd(self, ctx, *, query=None):
        """ Search for a vaguely relevant xkcd comic (if you're lucky). Otherwise returns a random comic. """
        if query:
            word_list = query.split(' ')
        else:
            word_list = None

        comic_dict = await self.bot.loop.run_in_executor(None, Comics.sync_get_xkcd, word_list)

        if comic_dict['random']:
            await ctx.send("Sorry, I didn't find anything. Here's a random comic:\n**{}**\n{}".format(comic_dict['title'], comic_dict['image_link']))
        else:
            await ctx.send('I found this comic with {} hit(s):\n**{}**\n{}'.format(comic_dict['hits'], comic_dict['title'], comic_dict['image_link']))


def setup(bot):
    bot.add_cog(Comics(bot))
