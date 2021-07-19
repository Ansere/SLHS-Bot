from typing import List

from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import base, session  # , servermember_assignments
from assignment import Assignment

servermember_assignments = Table('member-assignment', base.metadata,
                                 Column("servermember_id", Integer, ForeignKey("servermember.id")),
                                 Column("assignment_id", Integer, ForeignKey("assignment.id")),
                                 )

list_servermembers = []


class ServerMember(base):
    __tablename__ = "servermember"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    real_name = Column(String)
    discord_id = Column(Integer)
    description = Column(String, default="A SLHS Student.")

    assignments = relationship(
        "Assignment",
        secondary=servermember_assignments,
        backref="servermembers"
    )

    def __repr__(self):
        return f"Member(id = {self.id!r}, username = {self.username!r}, discord_id = {self.discord_id}"

    def set_real_name(self, name):
        self.real_name = name
    def set_description(self, description):
        self.description = description


def load_members(bot):
    global list_servermembers
    list_current_members = session.query(ServerMember)
    list_new_members = []
    try:
        guild = bot.get_guild(748995290006028399)
    except:
        print("Unable to fetch SLHS guild. Not in server?")
    for member in guild.members:
        if member.bot is False and not (member.id in [servermember.id for servermember in list_current_members]):
            list_new_members.append(ServerMember(discord_id=member.id, username=member.name))
    session.add_all(list_new_members)
    for num, member in enumerate([guild.get_member(member.discord_id) for member in list_new_members]):
        try:
            member.mention
        except:
            print(f"Member with rowid {num + 1} has an invalid id!")
            session.execute(select(ServerMember).where(id=num + 1)).delete()
    session.commit()
    list_servermembers = session.query(ServerMember)


def get_servermember_list():
    return list_servermembers

def get_server_member(id):
    return [servermember for servermember in list_servermembers if id == servermember.discord_id][0]
