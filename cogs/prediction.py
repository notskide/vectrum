import os
import discord
from discord.ext import commands
from discord import app_commands
from groq import AsyncGroq
from backend.vectrum_math import calculate_composite_risk
from backend.settings import (
    SUPERUSERS,
    get_server_thought_setting,
    set_server_thought_setting,
    is_admin_or_superuser
)

DISCLAIMER_TEXT = "\n\n> ⚠️ *Predictions are probabilistic estimations generated via mathematical risk models and AI synthesis, not guaranteed future outcomes.*"

class ThoughtView(discord.ui.View):
    def __init__(self, requester_id: int, thoughts: str):
        super().__init__(timeout=86400)
        self.requester_id = requester_id
        self.thoughts = thoughts if thoughts else "No thought process details available."

    @discord.ui.button(label="View Thought Process", style=discord.ButtonStyle.secondary, emoji="🧠")
    async def view_thoughts(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_requester = (interaction.user.id == self.requester_id)
        is_super = interaction.user.id in SUPERUSERS
        is_owner = (interaction.guild is not None and interaction.guild.owner_id == interaction.user.id)

        if is_requester or is_super or is_owner:
            content = f"🧠 **Thought Process / Analytical Reasoning:**\n```\n{self.thoughts[:1800]}\n```"
            await interaction.response.send_message(content, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ You do not have permission to view this thought process.",
                ephemeral=True
            )

class Prediction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    @app_commands.command(name="predict", description="Generate a concise probabilistic prediction and risk assessment.")
    async def predict(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        guild_id = interaction.guild_id or 0
        thoughts_enabled = get_server_thought_setting(guild_id)

        weather_val = 0.75  
        news_val = 0.65
        econ_val = 0.50

        math_res = calculate_composite_risk(weather_val, news_val, econ_val)

        prompt = (
            f"Scenario Query: {query}\n"
            f"Calculated Risk Index: {math_res['risk_index']}%\n"
            f"Model Confidence: {math_res['confidence']}%\n\n"
            "Instructions:\n"
            "1. Keep responses extremely concise, direct, and short. Omit lengthy filler.\n"
            "2. If the user query is time-based or asks when an event will occur, explicitly provide an approximate date or estimated timeframe.\n"
            "3. Enclose all internal reasoning and thought processes inside <thought>...</thought> tags.\n"
            "4. Following </thought>, provide the short final prediction summary."
        )

        try:
            response = await self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Vectrum, an advanced probabilistic risk engine. "
                            "Be direct, brief, and clear."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            raw_content = response.choices[0].message.content

            thoughts = ""
            if "<thought>" in raw_content and "</thought>" in raw_content:
                parts = raw_content.split("</thought>")
                thoughts = parts[0].replace("<thought>", "").strip()
                ai_summary = parts[1].strip()
            else:
                ai_summary = raw_content.strip()

            max_desc_len = 4096 - len(DISCLAIMER_TEXT) - 10
            if len(ai_summary) > max_desc_len:
                ai_summary = ai_summary[:max_desc_len - 3] + "..."

            embed = discord.Embed(
                title=f"Vectrum Assessment | {query[:200]}",
                color=discord.Color.dark_teal()
            )
            embed.add_field(name="Calculated Risk Index", value=f"**{math_res['risk_index']}%**", inline=True)
            embed.add_field(name="Model Confidence", value=f"**{math_res['confidence']}%**", inline=True)
            embed.description = ai_summary + DISCLAIMER_TEXT
            embed.set_footer(text="Vectrum Analytical Engine v1.0 • Powered by Qwen3.8-27B")

            if thoughts_enabled and thoughts:
                view = ThoughtView(interaction.user.id, thoughts)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while generating synthesis: `{e}`")

    @app_commands.command(name="toggle_thoughts", description="Enable or disable thought process visibility for this server.")
    async def toggle_thoughts(self, interaction: discord.Interaction, enabled: bool):
        guild_owner_id = interaction.guild.owner_id if interaction.guild else 0
        if not is_admin_or_superuser(interaction.user.id, guild_owner_id):
            await interaction.response.send_message(
                "❌ Only Superusers and the Server Owner can modify server settings.",
                ephemeral=True
            )
            return

        guild_id = interaction.guild_id or 0
        set_server_thought_setting(guild_id, enabled)
        status_str = "ENABLED" if enabled else "DISABLED"
        await interaction.response.send_message(
            f"✅ Thought process feature for this server is now **{status_str}**."
        )

async def setup(bot):
    await bot.add_cog(Prediction(bot))
