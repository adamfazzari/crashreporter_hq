
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from .. import db

Stat2BarPlot = Table("Stat2BarPlot", db.metadata,
                     Column("left_id", Integer, ForeignKey("statisticbarplot.id")),
                     Column("right_id", Integer, ForeignKey("statistic.id")))


class StatisticBarPlot(db.Model):

    __tablename__ = 'statisticbarplot'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False)
    application_name = Column(String(50), unique=False, default='')
    application_version = Column(Integer, unique=False, default='')
    statistics = relationship('Statistic', secondary=Stat2BarPlot, backref='plots')
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='barplots', foreign_keys=[group_id])

    def __init__(self, name, group, *statistics):
        self.name = name
        self.group = group
        self.statistics.extend(statistics)

