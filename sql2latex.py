import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, Column, JSON, BigInteger
from sqlalchemy.orm import relationship, Relationship
from sqlalchemy.sql.schema import ScalarElementColumnDefault, ForeignKey

from OJ import Base, BaseModel

caption = 'UserInfo数据字典'


class ClassName:
    __tablename__ = 'UserInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(200), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password = Column(String(200))
    is_admin = Column(Boolean, default=False)
    lastlogin = Column(DateTime, default=datetime.datetime.now())

    acm_problems_status = Column(JSON, default={})
    oi_problems_status = Column(JSON, default={})
    real_name = Column(String(30), nullable=True)
    accepted_number = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    submission_number = Column(Integer, default=0)


latex = r'''\begin{table}
\caption{%s}
\label{table:%s}
\begin{tabularx}{\textwidth}{|X|l|l|l|l|l|l|}
\hline
字段 & 类型 & Not null & Unique & Auto inc. & Primary key & Default \\ \hline
%s
Foreign Keys & \multicolumn{6}{|l|}{%s} \\ \hline
\end{tabularx}
\end{table}
'''

dic = {}
result = ''
foreign_key = ''

for key in ClassName.__dict__.keys():
    if '__' in key:
        continue
    item = ClassName.__getattribute__(ClassName, key)
    if item.__class__ == Relationship:
        continue
    key = key.replace('_', '\_')

    if item.foreign_keys:
        # foreign_key += r'\multicolumn{7}{|l|}{%s$\xrightarrow{}$%s} \\' % (key, list(item.foreign_keys)[0]._colspec) + '\n'
        foreign_key += key + ';'

    config = {
        'Type': item.__getattribute__('type'),
        'Not Null': not item.__getattribute__('nullable'),
        'Unique': item.__getattribute__('unique') if item.__getattribute__('unique') else '',
        'Auto Inc.': '' if item.__getattribute__('autoincrement') == 'auto' else item.__getattribute__('autoincrement'),
        'Primary Key': 'True' if item.__getattribute__('primary_key') else '',
        'Default': '',
    }
    config['Type'] = str(config['Type'])
    if '(' in config['Type']:
        config['Type'] = config['Type'][:config['Type'].index('(')]
    if config['Type'] == 'tinyint':
        config['Type'] = 'boolean'
    line = f'{key} & {config["Type"]} & {config["Not Null"]} & ' \
           f'{config["Unique"]} & {config["Auto Inc."]} & ' \
           f'{config["Primary Key"]} & {config["Default"]} \\\\ \\hline'
    result += line + '\n'
latex = latex % (caption, caption, result, foreign_key)
open('latex.txt', 'w', encoding='utf8').write(latex)
