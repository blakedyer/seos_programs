import streamlit as st
import pandas as pd
import numpy as np
import os
import graphviz
import base64
# import requests

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


st.set_page_config(page_title="SEOS Programs", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        width: 400px;
        margin-left: -400px;
    }

    """,
    unsafe_allow_html=True,
)

elective_color = "#7f8fa6"
requirement_color = "#487eb0"
pre_req_color = "#dcdde1"

st.title('SEOS Programs node graph')
course_path = 'data/courses/'
program_path = 'data/programs/'
simplification_path = 'data/simplifications/'

toggle2 = st.checkbox('Toggle me to rotate to left/right',value=False)
# toggle = st.checkbox('Toggle me to force some structure to course order:',value=False)
choices = os.listdir(program_path) + ['all EOS courses']
program_choice = st.selectbox('Which program?', choices, index=0)




simplifications = pd.read_csv(simplification_path+'simplifications.csv',index_col=0)
simplifications = simplifications.T

course_files = os.listdir(course_path)
course_files = [c for c in course_files if '~' not in c]
courses = {}

for c in course_files:
    course = c[:-4]
    courses[course]={}
    df = pd.read_csv(course_path+course+'.csv')
    for k in df.keys():
        for j in simplifications.keys():
            if j in list(df[k][1:].dropna().values):

                if len(simplifications[j].dropna())==1:
                    df[k][df[k]==j] = simplifications[j].dropna()[0]
                else:
                    df[df[k]==j] = simplifications[j].dropna()[0]
                    dict_add = {}
                    dict_add[k] = simplifications[j].dropna()[1]
                    df=df.append(dict_add,ignore_index=True)
    courses[course]['N Required'] = [df[k][0] for k in df.keys()]
    courses[course]['Options'] = [list(df[k][1:].dropna().values) for k in df.keys()]

# st.write(courses['EOS225'])

# st.write(courses['EOS240']['Options'])

# toggle2 = st.checkbox('Toggle me 2:',value=False)
# if toggle2:
#     for course in courses.keys():
#         for o in courses[course]['Options']:
#             if ('EOS130' in o) and ('GEOG130' in o):
#                 o.remove('GEOG130')

# _=courses.pop('EOS460', None)

u = graphviz.Digraph('unix', filename='flow', format='svg',
                     node_attr={'color': pre_req_color, 'style': 'filled', 'fontsize':'8', 'fontcolor': 'black'})


if program_choice != 'all EOS courses':
    program_df = pd.read_csv(program_path+program_choice)
# st.write(list(program_df[k][1:].dropna().values))
    label_1 = 'EOS Req'
    label_2 = 'EOS elective'
    for k in program_df.keys():
            for j in list(program_df[k][1:].dropna().values):
                if len(list(program_df[k][1:].dropna().values)) == int(program_df[k][0]):
                    u.attr('node', shape='ellipse', color=requirement_color, fontcolor='white')
                    u.node(j)
                else:
                    u.attr('node', shape='ellipse', color=elective_color, fontcolor='white')
                    u.node(j)
else:
    label_1 = 'EOS course'
    label_2 = 'Other course'
    eos_courses = os.listdir(course_path)
    eos_courses = [e for e in eos_courses if 'EOS' in e]
    for e in eos_courses:
        u.attr('node', shape='ellipse', color=requirement_color, fontcolor='white')
        node_name = e[:-4]
        u.node(node_name)

    # st.write(os.listdir(course_path))
scale = st.slider('Scale multiplier',min_value=.1,max_value=2.0,step=.1,value=1.0)
if toggle2:
    u.attr(rankdir='LR')
    u.attr(ranksep='.5')
    u.attr(dpi=f'{100*scale}')
else:
    u.attr(ranksep='.2')
    u.attr(dpi=f'{60*scale}')
u.attr('node', **{'color': pre_req_color, 'style': 'filled', 'fontsize':'8', 'fontcolor': 'black'})

for n in ['1','2','3','4']:
    with u.subgraph() as s:
        s.attr(rank='same')
        for course in courses.keys():
            if f'EOS{n}' in course:
                s.node(course)
one_of_colors = ['#e55039','#eb2f06','#b71540'] #reds
two_of_colors = ['#4a69bd','#1e3799','#0c2461'] #blues
three_of_colors = ['#78e08f','#38ada9','#079992'] #greens

styles = ['solid','dashed', 'dotted']

for course in courses.keys():
    n_list = []
    for subset,N in zip(courses[course]['Options'],courses[course]['N Required']):
        subset = list(set(subset))
        color = 0
        N = int(N)
        if len(subset) != N:
            if N in n_list:
                color+=1
            n_list.append(N)
        for req in subset:
            if len(subset) == N: #all
                u.edge(req,course)
            elif N==1:
                u.edge(req,course, style=styles[color], color=one_of_colors[color])
            elif N==2:
                u.edge(req,course, style=styles[color], color=two_of_colors[color])
            elif N==3:
                u.edge(req,course, style=styles[color], color=three_of_colors[color])
# u.edges([('EOS120','EOS210')])


u.attr('node', shape='ellipse', color=requirement_color, fontcolor='white')
u.node(label_1)
u.attr('node', shape='ellipse', color=elective_color, fontcolor='white')
u.node(label_2)
u.edge(label_1,label_2,label='required')
u.edge(label_1,label_2,style='solid',color=one_of_colors[0],label='1 required')
u.edge(label_1,label_2,style='solid',color=two_of_colors[0],label='2 required')
# u.edge('Program Requirement\n(EOS)','Program Elective\n(EOS)',style='solid',color=three_of_colors[0],label='3 required')

toggle=False
if toggle:
    with u.subgraph(name='cluster_physics',graph_attr={'color': 'transparent'}) as s:
        s.node('PHYS102')
        s.node('PHYS110/111')
        s.node('PHYS217')
        s.node('PHYS102B')
        s.node('PHYS120/130')
        s.node('PHYS317')
        s.node('PHYS111')
        s.node('PHYS130')
        s.node('PHYS110')
        s.node('PHYS120')

    with u.subgraph(name='cluster_math',graph_attr={'color': 'transparent'}) as s:
        s.node('MATH100')
        s.node('MATH102')
        s.node('MATH109')
        s.node('MATH204')
        s.node('MATH202')
        s.node('MATH101')

    with u.subgraph(name='cluster_chem',graph_attr={'color': 'transparent'}) as s:
        s.node('CHEM102')
        s.node('CHEM245')


    with u.subgraph(name='cluster_biol',graph_attr={'color': 'transparent'}) as s:
        s.node('BIOL184')
        s.node('BIOL150A')

    with u.subgraph(name='cluster_geog',graph_attr={'color': 'transparent'}) as s:
        s.node('GEOG130')
        s.node('GEOG103')



u.attr(label=f"{program_choice}")
w = u.unflatten(stagger=1)
# st.write(type(u))
# st.write(u.unflatten(stagger=2).view())
# render_svg(svg)
# st.write(u.unflatten(stagger=1).pipe(format='svg'))
u.attr(width='2')

svg = u.unflatten(stagger=1).pipe(format='svg')
# st.write(svg.decode("utf-8"))
# st.graphviz_chart(u, use_container_width=False)
# render_svg(svg.decode("utf-8"))
st.image(svg.decode("utf-8"))
