# OEM Gráfico Escala Técnica v2
# Cambiar únicamente estos límites si en el futuro cambian los criterios
LIMITES={
'critico':0.90,
'desgaste':1.00,
'seguimiento':1.10,
'normal':1.20,
'excelente':1.40
}

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from io import BytesIO

st.set_page_config(layout='wide')
st.title('OEM Insight - Escala Técnica v2')

st.sidebar.header('Datos')
equipo=st.sidebar.text_input('Equipo','GENSET 11')
horas=st.sidebar.text_input('Horas de operación','12000 h')
supervisor=st.sidebar.text_input('Supervisor','')
cil=st.sidebar.text_input('Cilindro','A1')
tipo=st.sidebar.selectbox('Tipo',['UPPER','LOWER'])

vals=[]
cols=st.columns(3)
for j,c in enumerate(cols):
    with c:
        st.markdown(f'**{"ABC"[j]}**')
        col=[]
        for i in range(5):
            col.append(st.number_input(f'{j}-{i}',1.15,format='%.2f',step=0.01,key=f'{j}{i}'))
        vals.append(col)
arr=np.array(vals).T

st.info("""Clasificación técnica
🟢 ≥1.20 Excelente/Normal
🟢 1.10–1.19 Normal
🟡 1.00–1.09 Seguimiento
🟠 0.90–0.99 Desgaste importante
🔴 <0.90 Desgaste severo""")

if st.button('Generar gráfico'):
    colors=['#b30000','#f57c00','#ffd54f','#7bc96f','#1b8f3a']
    bounds=[0.0,LIMITES['critico'],LIMITES['desgaste'],LIMITES['seguimiento'],LIMITES['normal'],LIMITES['excelente']]
    cmap=ListedColormap(colors)
    norm=BoundaryNorm(bounds,cmap.N)

    fig=plt.figure(figsize=(12,7),dpi=180)
    fig.text(0.04,0.95,'MEDICIÓN DE COJINETES BIG END BEARING',fontsize=17,fontweight='bold')
    fig.text(0.04,0.92,f'{equipo} | {cil} {tipo}',fontsize=10)
    fig.text(0.04,0.895,f'Horas: {horas} | Supervisor: {supervisor}',fontsize=9)

    ax=fig.add_axes([0.08,0.18,0.60,0.68])
    im=ax.imshow(arr.T,origin='lower',extent=[1,5,1,3],cmap=cmap,norm=norm,aspect='auto',interpolation='nearest')
    for i in range(5):
        for j in range(3):
            ax.scatter(i+1,j+1,s=40,c='white',edgecolors='black')
            ax.text(i+1,j+1,f'{arr[i,j]:.2f}',ha='center',va='center',fontsize=7)
    ax.set_xticks([1,2,3,4,5]);ax.set_yticks([1,2,3]);ax.set_yticklabels(['A','B','C'])

    cax=fig.add_axes([0.74,0.22,0.035,0.58])
    cb=plt.colorbar(im,cax=cax,boundaries=bounds,
                    ticks=[0.45,0.95,1.05,1.15,1.30])
    cb.ax.set_yticklabels([
        '<0.90  Desgaste severo',
        '0.90-0.99  Desgaste',
        '1.00-1.09  Seguimiento',
        '1.10-1.19  Normal',
        '≥1.20  Excelente'
    ],fontsize=8)

    st.pyplot(fig)
    bio=BytesIO()
    fig.savefig(bio,format='png',bbox_inches='tight')
    bio.seek(0)
    st.download_button('Descargar PNG',bio.getvalue(),'grafico_tecnico.png','image/png')
