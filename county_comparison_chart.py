"""Consistent, zero-based county comparisons with labeled values and units."""


def comparison_chart(orange, dutchess, label, maximum, suffix=''):
    import altair as alt
    import pandas as pd
    data = pd.DataFrame([
        {'County':'Orange', 'Value':orange, 'Label':f'{orange:g}{suffix}'},
        {'County':'Dutchess', 'Value':dutchess, 'Label':f'{dutchess:g}{suffix}'},
    ])
    base = alt.Chart(data).encode(
        y=alt.Y('County:N',sort=['Orange','Dutchess'],title=None,
                axis=alt.Axis(labelFontSize=15,labelPadding=10,ticks=False,domain=False)),
        x=alt.X('Value:Q',title=None,scale=alt.Scale(domain=[0,maximum],nice=False),
                axis=alt.Axis(labelFontSize=12,tickCount=4,grid=True)),
    )
    bars=base.mark_bar(size=32,cornerRadiusEnd=4).encode(
        color=alt.Color('County:N',scale=alt.Scale(domain=['Orange','Dutchess'],range=['#C65D17','#2474A6']),legend=None),
        tooltip=[alt.Tooltip('County:N'),alt.Tooltip('Label:N',title=label)],
    )
    labels=base.mark_text(align='left',dx=8,fontSize=15,fontWeight='bold').encode(text='Label:N')
    return (bars+labels).properties(height=150).configure_view(stroke=None)
