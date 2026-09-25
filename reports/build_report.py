"""Build the technical report (Spanish) as reports/informe_sistema_mundo.pdf.

Run after the model pipeline (results/*.json) and reports/figures.py.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
FIG = REP / "fig"
EQ = REP / "eq"
EQ.mkdir(exist_ok=True)
OUT = REP / "informe_sistema_mundo.pdf"

LIB = "/usr/share/fonts/truetype/liberation/"
DJ = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Serif", LIB + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", LIB + "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", LIB + "LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", LIB + "LiberationSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Sans", DJ + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B", DJ + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", DJ + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Serif", normal="Serif", bold="Serif-B", italic="Serif-I", boldItalic="Serif-BI")
registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans", boldItalic="Sans-B")

INK = colors.HexColor("#18222c")
ACC = colors.HexColor("#1f4f8f")
MUT = colors.HexColor("#5b6670")
RULE = colors.HexColor("#c9d1d8")
SOFT = colors.HexColor("#eef2f6")

ST = {
    "body": ParagraphStyle("body", fontName="Serif", fontSize=10.5, leading=14.6, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6),
    "h1": ParagraphStyle("h1", keepWithNext=1, fontName="Sans-B", fontSize=16, leading=20, textColor=ACC, spaceBefore=6, spaceAfter=10),
    "h2": ParagraphStyle("h2", keepWithNext=1, fontName="Sans-B", fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", keepWithNext=1, fontName="Sans-B", fontSize=9.8, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=3),
    "bullet": ParagraphStyle("bullet", fontName="Serif", fontSize=10.5, leading=14.2, alignment=TA_LEFT, textColor=INK, leftIndent=14, bulletIndent=3, spaceAfter=2.5),
    "cap": ParagraphStyle("cap", fontName="Sans", fontSize=8, leading=10.5, textColor=MUT, alignment=TA_LEFT, spaceBefore=3, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="Serif", fontSize=8.6, leading=10.8, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Sans-B", fontSize=7.6, leading=9.6, textColor=colors.white),
    "box": ParagraphStyle("box", fontName="Serif", fontSize=10, leading=13.8, textColor=INK, alignment=TA_JUSTIFY),
    "toc1": ParagraphStyle("toc1", fontName="Sans", fontSize=10, leading=15, leftIndent=0, textColor=INK),
    "toc2": ParagraphStyle("toc2", fontName="Serif", fontSize=9.5, leading=12.5, leftIndent=16, textColor=MUT),
}


def P(t, s="body"):
    return Paragraph(t, ST[s])


def H1(t):
    p = Paragraph(t, ST["h1"]); p._toc = (0, t); return p


def H2(t):
    p = Paragraph(t, ST["h2"]); p._toc = (1, t); return p


def H3(t):
    return Paragraph(t, ST["h3"])


def B(items):
    return [Paragraph(i, ST["bullet"], bulletText="•") for i in items]


def fig(name, caption, width=16.2):
    path = FIG / f"{name}.png"
    img = Image(str(path))
    r = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = width * cm, width * cm * r
    return KeepTogether([img, P(caption, "cap")])


_eq_n = [0]


def eq(tex, size=12.5):
    """Render a display equation with matplotlib mathtext, numbered."""
    _eq_n[0] += 1
    n = _eq_n[0]
    f = plt.figure(figsize=(0.01, 0.01))
    f.text(0, 0, f"${tex}$", fontsize=size, color="#18222c")
    path = EQ / f"eq{n:02d}.png"
    f.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.03, transparent=True)
    plt.close(f)
    img = Image(str(path))
    img.drawWidth, img.drawHeight = img.imageWidth * 72 / 300, img.imageHeight * 72 / 300
    if img.drawWidth > 14.5 * cm:
        k = 14.5 * cm / img.drawWidth
        img.drawWidth *= k; img.drawHeight *= k
    t = Table([[img, P(f"({n})", "cap")]], colWidths=[15 * cm, 1.2 * cm])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (0, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def table(rows, widths, header=True, zebra=True, font=None):
    data = [[Paragraph(str(c), ST["cellh"] if (header and i == 0) else ST["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    sty = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, -1), (-1, -1), 0.6, RULE),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        sty += [("BACKGROUND", (0, 0), (-1, 0), ACC)]
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                sty.append(("BACKGROUND", (0, i), (-1, i), SOFT))
    t.setStyle(TableStyle(sty))
    return t


def box(title, text):
    t = Table([[Paragraph(f"<b>{title}</b><br/>{text}", ST["box"])]], colWidths=[16.2 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("LINEBEFORE", (0, 0), (0, -1), 3, ACC),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 8)])


class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm,
                         title="Atlas del Sistema-Mundo: informe técnico", author="Modelo agéntico sistema-mundo", **kw)
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate("cover", [fr], onPage=self.cover), PageTemplate("body", [fr], onPage=self.deco)])

    def cover(self, c, doc):
        c.saveState()
        c.setFillColor(colors.HexColor("#0f2a4a")); c.rect(0, A4[1] - 9.5 * cm, A4[0], 9.5 * cm, fill=1, stroke=0)
        c.restoreState()

    def deco(self, c, doc):
        c.saveState()
        c.setStrokeColor(RULE); c.setLineWidth(0.5)
        c.line(2.3 * cm, A4[1] - 1.6 * cm, A4[0] - 2.3 * cm, A4[1] - 1.6 * cm)
        c.setFont("Sans", 7.5); c.setFillColor(MUT)
        c.drawString(2.3 * cm, A4[1] - 1.4 * cm, "Atlas del Sistema-Mundo · Informe técnico")
        c.drawRightString(A4[0] - 2.3 * cm, 1.3 * cm, f"{doc.page}")
        c.restoreState()

    def afterFlowable(self, f):
        if hasattr(f, "_toc"):
            lvl, text = f._toc
            key = f"h{id(f)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text.replace("&amp;", "&"), key, level=lvl, closed=lvl > 0)
            self.notify("TOCEntry", (lvl, text, self.page, key))


# ----------------------------------------------------------------------------- data
cal = json.load(open(ROOT / "results" / "calibration.json"))
D = json.load(open(ROOT / "results" / "dashboard_data.json"))
S = json.load(open(ROOT / "results" / "summary.json"))["resumen"]
REC = json.load(open(ROOT / "results" / "recomendaciones.json"))
V = D["validacion"]
IRL = D["irl"]
E1 = cal["etapa1"]
FR = cal["libres"]
fit = cal["fit"]
f2 = lambda x: f"{x:.2f}".replace(".", ",")
f3 = lambda x: f"{x:.3f}".replace(".", ",")
pc = lambda x: f"{100 * x:.0f} %"
pc1 = lambda x: f"{100 * x:.1f} %".replace(".", ",")

story = []

# ----------------------------------------------------------------------------- cover
story += [Spacer(1, 1.2 * cm),
          Paragraph("INFORME TÉCNICO", ParagraphStyle("k", fontName="Sans", fontSize=9, textColor=colors.HexColor("#9fc3ee"), leading=12)),
          Spacer(1, 6),
          Paragraph("Atlas del Sistema-Mundo", ParagraphStyle("t", fontName="Sans-B", fontSize=30, leading=34, textColor=colors.white)),
          Spacer(1, 8),
          Paragraph("Un modelo agéntico híbrido del desarrollo desigual, la inestabilidad política y los límites físicos, "
                    "calibrado con datos de 1950–2019 y proyectado a 2030",
                    ParagraphStyle("s", fontName="Serif-I", fontSize=13, leading=17, textColor=colors.HexColor("#dbe7f5"))),
          Spacer(1, 3.6 * cm)]
story += [P("Este informe explica, de principio a fin, qué se construyó y qué se aprendió. Primero presenta la teoría detrás de cada bloque del "
            "modelo; después, cómo se traduce en ecuaciones, con qué datos se calibra, cómo se infiere la manera en que deciden los países "
            "(problema inverso), qué tan bien pronostica fuera de muestra, qué políticas emergen al optimizar distintos objetivos y qué "
            "recomendaciones incrementales produce. Cada resultado va acompañado de su grado de confianza y de sus límites.")]
story += [Spacer(1, 0.6 * cm), table([
    ["Elemento", "Detalle"],
    ["Cobertura", "180 países, datos anuales 1950–2019, proyección 2020–2030"],
    ["Teorías", "Sistema-mundo (Wallerstein, Emmanuel, Amin), demografía estructural (Goldstone, Turchin), frontera metaétnica "
                "(Turchin), agotamiento logístico (Hubbert), deuda y crisis, instituciones, clima (Burke–Hsiang–Miguel)"],
    ["Métodos", "Modelo basado en agentes · calibración en dos etapas · clonación de conducta · aprendizaje por refuerzo inverso "
                "(Bajari–Benkard–Levin) · validación con orígenes rodantes · PPO · RL anclado a la conducta"],
    ["Código", "github.com/QU01/Reproducible-Research-Project-2 (rama claude/world-systems-agent-model-p0omqe)"],
    ["Fecha", "Septiembre de 2026"]], [3.2, 13.0])]
story += [NextPageTemplate("body"), PageBreak()]

# ----------------------------------------------------------------------------- TOC
toc = TableOfContents()
toc.levelStyles = [ST["toc1"], ST["toc2"]]
story += [Paragraph("Contenido", ST["h1"]), toc, PageBreak()]

# ----------------------------------------------------------------------------- executive summary
story += [H1("Resumen ejecutivo")]
story += [P("Se construyó un modelo en el que cada país es un agente que, año con año, produce con capital, trabajo, tecnología y "
            "recursos naturales, comercia con el resto del mundo, reparte su excedente entre élites y masas y decide cómo gastar. "
            "El modelo une tres tradiciones que rara vez se combinan: la teoría del sistema-mundo (el excedente fluye de la periferia "
            "al centro), la teoría demográfico-estructural (la sobreproducción de élites y el empobrecimiento relativo de las masas "
            "generan estrés político e inestabilidad) y la teoría de la frontera metaétnica (la cohesión colectiva, o asabiya, nace en "
            "las fronteras y se erosiona en los centros ricos). A esto se suman el agotamiento de recursos, la deuda y las crisis "
            "financieras, las instituciones políticas y el clima.")]
story += [P("<b>Qué se hizo.</b>")]
story += B(["Se reunieron más de 500 variables por país-año de fuentes abiertas (PWT, Banco Mundial, UCDP, V-Dem, WID, Global Macro "
            "Database, COW, OWID, Global Carbon Project, entre otras) y se estimaron directamente con datos todos los mecanismos observables "
            "(golpes de Estado, transiciones de régimen, crisis, reacción fiscal, nacionalizaciones y financiamiento externo).",
            "Los 23 parámetros estructurales restantes se calibraron por evolución diferencial, comparando 70 años de trayectorias "
            "simuladas con los datos.",
            "Se resolvió el <i>problema inverso</i>: primero se estimó de los datos la regla con la que cada país reparte su gasto; después "
            "se buscó qué recompensa hace que esa conducta observada sea mejor que sus alternativas.",
            "Se validó el modelo fuera de muestra desde 49 años de origen (1970–2018) a 1, 5 y 10 años, con parámetros estimados solo con el "
            "pasado, contra referencias estadísticas y apagando cada bloque teórico por separado.",
            "Se entrenaron políticas óptimas por aprendizaje por refuerzo (PPO) para cuatro objetivos y, finalmente, recomendaciones "
            "incrementales ancladas a la conducta real de cada país."])
story += [P("<b>Qué se encontró.</b>")]
story += B([f"<b>Los países deciden con mucha inercia.</b> La persistencia anual de su gasto va de 0,79 a 0,97 (escala logit). La "
            f"recompensa que mejor explica su conducta combina inercia (0,84) y poder relativo (0,47), con peso negativo en el consumo "
            f"(−0,28); explica el {pc(IRL['racionalidad'])} de las comparaciones frente a un 50 % al azar.",
            f"<b>A 5 y 10 años el modelo pronostica el ingreso mejor que las referencias estadísticas</b> en términos probabilísticos (CRPS "
            f"{f3(V['gdp']['5']['completo']['crps'])} y {f3(V['gdp']['10']['completo']['crps'])} frente a 0,127 y 0,215), y ordena mejor quién crece "
            f"más. También gana en deuda y temperatura global. A 1 año pierde contra un AR(1) y en conflicto armado pierde contra un "
            f"logit histórico simple.",
            "<b>Los bloques teóricos aportan poco a la predicción a corto plazo.</b> Deuda y crisis, clima e instituciones mejoran algo el "
            "PIB a 10 años; la frontera metaétnica mejora la predicción de conflicto. El sistema-mundo y la demografía estructural casi no "
            "cambian el pronóstico, y el índice de estrés político (PSI) casi no predice conflicto una vez que se controla por ingreso, "
            "rentas de recursos y cohesión.",
            "<b>Optimizar sin restricciones produce políticas extremas.</b> Sin financiamiento, el RL llevaba el 92–95 % del gasto al capital. "
            "Con ahorro, crédito externo y costos de ajuste, las políticas se diferencian: bienestar gasta menos y se vuelve acreedor, "
            "poder gasta y se endeuda, élite redistribuye.",
            "<b>Las recomendaciones ancladas son robustas en signo pero no deben usarse todavía.</b> Con objetivo de bienestar recomiendan "
            "gastar unos 10 puntos del PIB menos, sobre todo en capital: un 6–8 % más de consumo en la década y un 6,6 % menos de PIB a 10 años. El resultado depende de un "
            "costo de ajuste calibrado que parece demasiado alto."])
story += [box("Conclusión central",
              "El modelo es útil para entender mecanismos y para pronosticar distribuciones de ingreso a mediano plazo, pero todavía no es "
              "una herramienta de recomendación de políticas. Su valor más sólido es mostrar qué teorías ayudan a predecir (deuda, clima, "
              "instituciones, frontera metaétnica para el conflicto) y cuáles, tal como están formuladas, no añaden información (el PSI como "
              "predictor directo de conflicto, los flujos del sistema-mundo para el crecimiento de corto plazo).")]
story += [PageBreak()]

# ----------------------------------------------------------------------------- 1. question
story += [H1("1. Pregunta y enfoque")]
story += [P("¿Por qué algunos países convergen hacia el ingreso de los más ricos y otros no? ¿Qué papel juegan las transferencias de "
            "valor entre países, la competencia entre élites, la cohesión social, los recursos naturales, la deuda y el clima? ¿Cómo "
            "deciden realmente los gobiernos y qué deberían hacer si persiguieran objetivos explícitos? Estas preguntas cruzan la economía "
            "del desarrollo, la sociología histórica y la ciencia política, y cada tradición ofrece piezas del rompecabezas que rara vez se "
            "ponen juntas y se contrastan con los mismos datos.")]
story += [P("Se eligió un <b>modelo basado en agentes</b> por tres razones. Primero, la heterogeneidad importa: 180 países con "
            "trayectorias, recursos e instituciones distintas no se resumen bien con un agente representativo. Segundo, las interacciones "
            "son el mecanismo: el intercambio desigual, las concesiones extractivas y el precio mundial de los recursos conectan a unos "
            "países con otros. Tercero, los procesos clave son no lineales y estocásticos (golpes, crisis, saltos tecnológicos, conflictos), "
            "así que interesa la distribución de resultados, no solo su promedio.")]
story += [P("El trabajo siguió cinco pasos, que ordenan este informe: construir el modelo a partir de la teoría (secciones 2 y 3); "
            "reunir datos y calibrar (4 y 5); inferir cómo deciden los países (6); validar fuera de muestra (7); y usar el modelo para "
            "explorar políticas óptimas y recomendaciones (8 y 9). Las secciones 10 a 13 cubren clima y conflicto, la proyección a 2030, "
            "la visualización, y las conclusiones y límites.")]
story += [fig("f01_arquitectura", "Figura 1. Arquitectura del modelo. Cada país decide cómo gastar; las decisiones alimentan la tecnología, "
                                  "los recursos y la deuda; los flujos entre centro y periferia redistribuyen el excedente, y el reparto entre "
                                  "élites y masas determina el estrés político y el riesgo de conflicto.", 15.5)]

# ----------------------------------------------------------------------------- 2. theory
story += [PageBreak(), H1("2. Fundamentos teóricos")]
story += [P("Cada bloque del modelo traduce una teoría a mecanismos que se pueden simular y contrastar. Esta sección explica la intuición "
            "de cada teoría, cómo se representa y qué dice la evidencia empírica usada para anclarla.")]

story += [H2("2.1 Sistema-mundo: el excedente fluye hacia el centro")]
story += [P("Para Immanuel Wallerstein la economía mundial capitalista es un sistema único dividido en <b>centro</b>, "
            "<b>semiperiferia</b> y <b>periferia</b>. El centro concentra las actividades de alta productividad y alto margen; la periferia "
            "exporta bienes de bajo valor agregado. La posición no es fija, pero moverse es difícil porque el propio intercambio reproduce "
            "la jerarquía. Arghiri Emmanuel formalizó el <b>intercambio desigual</b>: cuando los salarios difieren mucho entre países, los "
            "precios internacionales transfieren valor del país de salarios bajos al de salarios altos, aunque el comercio sea voluntario. "
            "Samir Amin añadió las <b>rentas de monopolio</b> sobre bienes tecnológicos y los flujos financieros (intereses, beneficios "
            "repatriados) como canales adicionales.")]
story += [P("En el modelo, la centralidad de cada país es una función suave de su productividad relativa (el 20 % más productivo es el "
            "centro). La periferia pierde una fracción de su producción comerciada con cada socio del centro en proporción a la brecha de "
            "niveles de precios (efecto Penn), usando la red real de comercio bilateral (Correlates of War, 1950–2014). Además paga una renta "
            "de monopolio sobre los bienes de alto valor que importa y los intereses de su deuda externa. Los estudios recientes de Hickel "
            "et al. (2022) estiman que en 2015 el centro se apropió, incorporados en el comercio, de 12 Gt de materiales, 822 Mha de tierra, "
            "21 EJ de energía y 188 millones de años-persona de trabajo.")]

story += [H2("2.2 Demografía estructural: élites, masas y Estado")]
story += [P("Jack Goldstone (1991) y Peter Turchin (2009, 2016) explican las oleadas de inestabilidad por tres fuerzas que se refuerzan: "
            "el <b>empobrecimiento relativo de las masas</b> (salarios que no siguen al producto, protuberancia juvenil), la "
            "<b>sobreproducción de élites</b> (más aspirantes a posiciones de élite que posiciones disponibles, lo que intensifica la "
            "competencia intraélite) y la <b>debilidad fiscal del Estado</b>. Turchin las resume en el Índice de Estrés Político:")]
story += [eq(r"\mathrm{PSI} = \mathrm{MMP}\times \mathrm{EMP}\times \mathrm{SFD}")]
story += [P("donde MMP es el potencial de movilización de masas, EMP el de movilización de élites y SFD la angustia fiscal del Estado. En "
            "el modelo, las élites capturan una fracción <i>E</i> del producto (anclada en la participación del 10 % más rico de WID) y una "
            "fracción mayor de las rentas de recursos y de las rentas que entran del exterior, sobre todo en autocracias. Cuando el ingreso "
            "por miembro de la élite es alto respecto al de las masas, el número de élites crece; cuando el ingreso de las masas se estanca "
            "frente a su promedio reciente, sube su movilización. El PSI entra en el riesgo de conflicto civil.")]

story += [H2("2.3 Frontera metaétnica y asabiya")]
story += [P("Ibn Jaldún llamó <i>asabiya</i> a la capacidad de un grupo para actuar colectivamente. Turchin (2003) propuso que la asabiya "
            "crece en las <b>fronteras metaétnicas</b>, donde un grupo enfrenta a otro muy distinto, y decae en los centros de imperios "
            "ricos y pacificados, donde la competencia se vuelve interna. En el modelo, la frontera de un país periférico es su exposición a "
            "un centro que lo drena: apertura comercial, rentas extraídas y concesiones extranjeras. La asabiya crece logísticamente con esa "
            "exposición y decae en países ricos, más rápido cuando hay sobreproducción de élites. Una asabiya alta mejora la eficiencia de "
            "la inversión, la probabilidad de saltos tecnológicos y la resistencia a la inestabilidad; también hace más difícil ceder "
            "recursos a extranjeros (nacionalismo de recursos). La asabiya inicial se toma de proxies de cohesión y capacidad estatal.")]

story += [H2("2.4 Recursos naturales: Hubbert y la maldición de los recursos")]
story += [P("M. King Hubbert observó que la producción de un recurso finito sigue una curva en forma de campana: sube mientras se abren "
            "yacimientos y cae cuando se agotan. En el modelo, cada país tiene unos recursos recuperables últimos y una capacidad bruta de "
            "extracción logística en lo ya extraído. El capital extractivo nacional y el extranjero compiten por esa misma capacidad: una "
            "concesión extranjera se queda con parte de la producción, acelera el agotamiento y reduce lo que el país puede explotar por sí "
            "mismo. El recurso es un insumo de la producción con precio mundial de equilibrio; quien no controla sus recursos paga un "
            "sobrecosto por importarlos. La literatura de la <b>maldición de los recursos</b> (Collier y Hoeffler 2004; Ross 2015) motiva "
            "dos efectos: las élites capturan más renta de recursos que de otros ingresos, y las rentas elevan el riesgo de conflicto. Las "
            "nacionalizaciones siguen el modelo de Guriev, Kolotilin y Sonin (2011): son más probables tras subidas del precio del petróleo.")]

story += [H2("2.5 Deuda, crisis y financiamiento")]
story += [P("Reinhart y Rogoff documentaron la <b>intolerancia a la deuda</b>: los países emergentes entran en problemas con niveles de "
            "deuda que los ricos soportan sin dificultad. El modelo usa una regla de reacción fiscal estimada (la deuda revierte a su media, "
            "baja con el crecimiento y sube en las crisis) más el efecto de la tasa real mundial. Las crisis financieras (Laeven y Valencia) "
            "siguen un logit estimado que depende de la deuda sobre el umbral, la tasa de interés de EE. UU., el crecimiento y el contagio, y "
            "dejan una pérdida permanente de producto. El bloque de <b>financiamiento</b> se apoya en el hallazgo de Feldstein y Horioka "
            "(1980): la inversión y el ahorro nacionales se mueven juntos, así que gastar más exige consumir menos o endeudarse con el exterior, "
            "y el crédito externo tiene límites. La inversión también está sujeta a <b>costos de ajuste</b> (Hayashi 1982): invertir mucho "
            "más de lo normal rinde menos.")]

story += [H2("2.6 Instituciones y geopolítica")]
story += [P("Los golpes de Estado se concentran en países pobres, con bajo crecimiento y con golpes recientes (la <b>trampa del golpe</b>, "
            "Londregan y Poole), y fueron más frecuentes durante la Guerra Fría (Powell y Thyne). Las transiciones a la democracia y los "
            "quiebres democráticos dependen del ingreso, del crecimiento y de la proporción de democracias en el mundo. Acemoglu, Naidu, "
            "Restrepo y Robinson (2019) estiman que la democratización eleva el PIB per cápita en torno a un 20 % a largo plazo; el modelo "
            "incorpora ese impulso gradual a la productividad. Las democracias parciales (anocracias) son las más inestables (Goldstone et "
            "al. 2010, Political Instability Task Force).")]

story += [H2("2.7 Tecnología: convergencia condicionada y saltos")]
story += [P("Siguiendo a Gerschenkron y a la literatura de convergencia condicionada, la productividad de cada país se acerca a la frontera "
            "tecnológica más rápido cuanto más lejos está, siempre que tenga <b>capacidad de absorción</b> (capital humano, Nelson y Phelps; "
            "Borensztein et al. 1998). La difusión se acelera con importaciones de bienes de alto valor (Coe y Helpman) y con inversión "
            "extranjera directa. Además hay <b>saltos tecnológicos estocásticos</b>: su probabilidad crece con el esfuerzo propio de I+D y "
            "educación y con la asabiya, y su tamaño con la distancia a la frontera. Así se representa la industrialización que sustituye "
            "importaciones.")]

story += [H2("2.8 Clima y ecología")]
story += [P("Burke, Hsiang y Miguel (2015) mostraron que el crecimiento responde de forma no lineal a la temperatura, con un óptimo cercano "
            "a 13 °C: los países cálidos y pobres pierden más. El modelo acumula ese daño con persistencia parcial. La temperatura global "
            "responde a las emisiones acumuladas mediante la respuesta climática transitoria a las emisiones (TCRE, 0,46 °C por 1000 GtCO₂ "
            "en nuestros datos); la de cada país la sigue con su propio factor de escala. Los desastres destruyen capital con mayor "
            "frecuencia a medida que se calienta el planeta, y un stock de capital natural se degrada cuando la huella ecológica supera la "
            "biocapacidad.")]

# ----------------------------------------------------------------------------- 3. model
story += [H1("3. El modelo")]
story += [H2("3.1 Agentes, tiempo y estado")]
story += [P("Hay 180 agentes (países) que entran al modelo cuando aparecen en las Penn World Tables. El paso es anual. Cada país tiene un "
            "estado con capital físico <i>K</i>, productividad <i>A</i>, capital humano <i>h</i> y población <i>L</i> (exógenos, de datos), "
            "participación de la élite <i>E</i>, número relativo de élites <i>n<sub>e</sub></i>, asabiya <i>S</i>, recursos últimos <i>U</i> "
            "y extraídos <i>X</i>, capital extractivo propio y extranjero, deuda, régimen político, conflicto, daño climático y capital "
            "natural. Se simulan en paralelo entre 8 y 48 mundos con números aleatorios distintos para obtener distribuciones.")]
story += [H2("3.2 Decisiones")]
story += [P("Cada año, cada país decide cuánto gastar y cómo repartirlo entre seis canales, como fracción del PIB:")]
story += [table([["Canal", "Qué representa", "Efecto en el modelo"],
                 ["k · Capital doméstico", "Formación bruta de capital fijo", "Aumenta K (con costos de ajuste)"],
                 ["r · Tecnología propia", "I+D y educación pública", "Eleva la probabilidad de saltos tecnológicos"],
                 ["m · Importar del centro", "Bienes manufacturados de alto valor", "Difusión tecnológica; paga renta de monopolio"],
                 ["x · Extracción propia", "Capital extractivo nacional", "Extrae más recursos propios; acelera el agotamiento"],
                 ["f · Recursos fuera", "Inversión en recursos de otros países", "Concesiones que compiten con el anfitrión"],
                 ["w · Redistribuir", "Transferencias y gasto social", "Sube el ingreso de las masas; baja la captura de élites"]],
                [3.6, 5.2, 7.4])]
story += [P("Hay tres formas de generar estas decisiones: las <b>acciones observadas</b> en los datos (modo histórico), la <b>regla de "
            "decisión estimada</b> por clonación de conducta (sección 6) y las <b>políticas aprendidas</b> por refuerzo (secciones 8 y 9).")]

story += [H2("3.3 Producción y recursos")]
story += [P("La producción combina capital, recursos y trabajo efectivo en una Cobb-Douglas. La participación de los recursos "
            "ψ<sub>t</sub> es la participación mundial observada de las rentas en el PIB, de modo que el modelo explica cómo se reparten "
            "las rentas entre países, no los ciclos del petróleo.")]
story += [eq(r"Y_i = A_i\,K_i^{\alpha}\,R_i^{\psi_t}\,(h_i L_i)^{1-\alpha-\psi_t},\qquad \alpha = 0.35")]
story += [P("La capacidad bruta de extracción es logística en la fracción ya extraída <i>x = X/U</i>, y la extracción efectiva satura con "
            "el capital extractivo (propio más extranjero):")]
story += [eq(r"\mathrm{Cap}_i = r_R\,U_i\,(x_i+\varepsilon)(1-x_i),\qquad \mathrm{Ext}_i = \mathrm{Cap}_i\left(1-e^{-K^R_i/(c_R\,\mathrm{Cap}_i)}\right)")]
story += [P("Un precio mundial iguala la demanda de recursos (derivada de la Cobb-Douglas de todos los países) con la extracción total.")]

story += [H2("3.4 Flujos del sistema-mundo")]
story += [P("La centralidad es una función logística de la distancia al percentil 80 del log del ingreso. El drenaje de la periferia <i>i</i> "
            "hacia el centro <i>j</i> usa la cuota de exportaciones bilaterales S<sub>ij</sub> y la brecha de niveles de precios:")]
story += [eq(r"c_i = \sigma\!\left(\frac{\ln y_i - q_{80}}{s}\right),\qquad \mathrm{Drain}_{ij} = \theta_d\,X_i\,S_{ij}\,\max\!\left[(y_j/y_i)^{\beta_{px}}-1,\,0\right] c_j\,(1-c_i)")]
story += [P("A esto se suman la renta de monopolio μ sobre los bienes de alto valor comprados al centro, los beneficios repatriados de las "
            "concesiones extranjeras y los intereses de la deuda externa. El ingreso nacional es el PIB más rentas recibidas menos rentas "
            "pagadas.")]

story += [H2("3.5 Élites, masas y estrés político")]
story += [P("El ingreso de la élite es su parte del producto no extractivo más una parte mayor de las rentas de recursos y de las rentas "
            "que entran. Las élites crecen cuando su ingreso relativo <i>v</i> supera el de referencia:")]
story += [eq(r"n_e' = n_e\,\exp\!\left[\beta_e\left(\frac{v}{v_0}-n_e\right)\right],\qquad \mathrm{EMP}=\frac{n_e^2}{v/v_0}")]
story += [eq(r"\mathrm{MMP}=\frac{1}{w_{rel}}\,e^{\,b_Y(\mathrm{juventud}-28)}\left(\frac{\overline{c}_{masas}}{c_{masas}}\right)^{\kappa},\qquad \mathrm{SFD}=(1.5-S)\left[1+\sigma\!\left(4\left(\frac{d}{d^*}-1\right)\right)+0.5\,\mathrm{crisis}\right]")]
story += [P("Redistribuir (canal <i>w</i>) sube el ingreso de las masas y reduce la captura de élites; las rentas la aumentan.")]

story += [H2("3.6 Conflicto civil")]
story += [P("La probabilidad de que empiece un conflicto armado es un logit que combina el PSI, el ingreso, la asabiya, las rentas de "
            "recursos, la anocracia y las anomalías de temperatura. Un conflicto en curso persiste con probabilidad alta, destruye producto "
            "y productividad y reduce la élite.")]
story += [eq(r"P(\mathrm{inicio}) = \sigma\!\left(b_0 + b_1\ln \mathrm{PSI} + b_2(\ln y-9) + b_3(S-0.5) + b_4\,\mathrm{rentas} + b_5\,4p(1-p) + \gamma\,z_T\right)")]

story += [H2("3.7 Asabiya")]
story += [eq(r"S' = S + r_a\,F\,S(1-S) - d_a\,(1-F)\,\rho(y)\,S\,n_e - 0.03\,\mathrm{conflicto}\cdot S")]
story += [P("<i>F</i> es la intensidad de frontera (apertura periférica más drenaje, renta de monopolio y extracción extranjera como "
            "fracción del PIB) y ρ(<i>y</i>) una logística que se activa en países ricos.")]

story += [H2("3.8 Tecnología")]
story += [eq(r"\Delta\ln A = g_0 + \mathrm{brecha}\cdot\left(\frac{h}{h_{90}}\right)^{\phi_h}\!\left(\kappa+\kappa_m\,m+\kappa_f\,\mathrm{IED}\right) + \mathrm{ayuda} + \sigma_a\varepsilon + \mathrm{saltos}")]
story += [P("Los saltos llegan con tasa de Poisson λ = λ<sub>0</sub>·√<i>r</i>·(0,5 + <i>S</i>) y tienen tamaño exponencial con media "
            "<i>j</i><sub>0</sub>(1 + brecha). Crisis, golpes y conflictos restan productividad; la democracia la suma gradualmente.")]

story += [H2("3.9 Deuda, crisis y financiamiento")]
story += [P("La deuda sigue la regla estimada más el efecto de la tasa mundial. El gasto por encima de la trayectoria de referencia "
            "(Δ<i>B</i>) se paga en una fracción η con ahorro propio y el resto con deuda externa, hasta un techo de déficit; el exceso es un "
            "recorte forzado del consumo. La deuda externa adicional paga intereses y se amortiza en unos diez años.")]
story += [eq(r"\Delta d = a + b\,d + c\,g + e\,\mathrm{crisis} + (r^*-\bar r)\,d,\qquad \mathrm{deuda\ externa} = \min\!\left[(1-\eta)\,\Delta B,\ \max(\bar{c}+CA_{ref},0)\right]")]
story += [eq(r"K' = (1-\delta)K + I - \frac{\chi}{2}\left(\frac{I}{K}-\delta-0.04\right)^{2}K")]

story += [H2("3.10 Clima y ecología")]
story += [eq(r"D_i' = \rho_D D_i + h(T_i) - h(\bar T_i),\quad h(T)=b_1T+b_2T^2,\qquad T_g' = T_g + \mathrm{TCRE}\cdot(\mathrm{CO}_2^{fosil}+\mathrm{CO}_2^{suelo})")]
story += [P("Las emisiones salen de la extracción fósil simulada. El daño acumulado <i>D</i> resta a la productividad; el capital natural "
            "se regenera lentamente y se degrada con el exceso de huella ecológica y el calentamiento local.")]

story += [H2("3.11 Modo observado y modo pronóstico")]
story += [P("Hasta el año de corte el modelo toma de los datos las instituciones, las crisis y la temperatura (modo observado). Después "
            "(modo pronóstico) los golpes, los cambios de régimen, las crisis, las nacionalizaciones, el clima y los desastres se vuelven "
            "endógenos, y las series exógenas quedan congeladas en su último valor, salvo la población. En cada paso se usan los mismos "
            "sorteos aleatorios para comparar políticas (números aleatorios comunes): dos simulaciones que solo difieren en una decisión "
            "difieren solo por su efecto.")]

# ----------------------------------------------------------------------------- 4. data
story += [PageBreak(), H1("4. Datos")]
story += [P("Ocho investigaciones paralelas, una por bloque, reunieron y documentaron las fuentes (notas en <font face='Mono' size='8.5'>"
            "docs/research/</font>). Todo se une en un panel de 180 países × 70 años con 513 variables. Los datos brutos no se versionan; "
            "los cargadores los vuelven a descargar.")]
story += [table([["Bloque", "Fuentes principales"],
                 ["Producción y capital", "Penn World Table 10.01 (PIB, capital, capital humano, niveles de precios)"],
                 ["Acciones de los países", "WDI (formación de capital, importaciones de manufacturas, I+D, educación, IED saliente, gasto social)"],
                 ["Élites y desigualdad", "World Inequality Database (10 % más rico), SWIID, Barro-Lee, ONU WPP 2024 (protuberancia juvenil)"],
                 ["Comercio y flujos", "Correlates of War Dyadic Trade 1950–2014, ECI (complejidad), IED"],
                 ["Recursos", "Rentas del Banco Mundial, OWID energía, reservas, yacimientos gigantes, nacionalizaciones (Guriev et al., curado)"],
                 ["Deuda y crisis", "Global Macro Database, IMF HPDD, Laeven-Valencia, Jordà-Schularick-Taylor, cuenta corriente"],
                 ["Instituciones", "V-Dem (Regimes of the World, poliarquía), Powell-Thyne (golpes), Archigos, ATOP, ayuda oficial (WDI)"],
                 ["Conflicto", "UCDP/PRIO Armed Conflict Dataset; UCDP GED v24.1 (eventos geolocalizados, 1989–2023)"],
                 ["Clima y ecología", "OWID CO₂, Global Carbon Project, HadCRUT/GISTEMP, UDel/FAO (temperatura local), EM-DAT, Global Footprint Network"],
                 ["Capas OSINT", "WRI centrales, Global Energy Monitor, OpenFlights, rutas marítimas AIS, TeleGeography, World Port Index"]],
                [3.8, 12.4])]
story += [P("Hay limitaciones de acceso: el entorno de cómputo solo alcanzaba GitHub, PyPI y npm, así que algunas fuentes se obtuvieron de "
            "copias públicas o de subconjuntos; cada nota de investigación indica cuáles.", "body")]

# ----------------------------------------------------------------------------- 5. calibration
story += [H1("5. Calibración")]
story += [P("La calibración tiene dos etapas. La idea es estimar directamente con datos todo lo que se observa y dejar para la "
            "simulación solo lo que no se observa (latente) o lo que depende de la interacción de muchos mecanismos.")]
story += [H2("5.1 Etapa 1: submodelos estimados con datos")]
g, ad, da, cr, de, na, fi = (E1[k]["coef"] for k in ("golpes", "transicion_ad", "transicion_da", "crisis", "deuda", "nacionalizacion", "financiamiento"))
story += [table([["Submodelo", "Método y n", "Coeficientes principales", "Lectura"],
                 ["Golpes de Estado", f"Logit, n = {E1['golpes']['n']:,}".replace(",", " "),
                  f"trampa +{f2(g['trampa'])}; Guerra Fría +{f2(g['guerra_fria'])}; democracia {f2(g['democracia'])}; crecimiento {f2(g['g'])}",
                  "Un golpe reciente casi triplica el riesgo; la Guerra Fría lo duplica."],
                 ["Autocracia → democracia", f"Logit, n = {E1['transicion_ad']['n']:,}".replace(",", " "),
                  f"ingreso +{f2(ad['ell'])}; % democracias +{f2(ad['W_D'])}", "Contagio democrático entre países."],
                 ["Democracia → autocracia", f"Logit, n = {E1['transicion_da']['n']:,}".replace(",", " "),
                  f"ingreso {f2(da['ell'])}; crecimiento {f2(da['g'])}", "Las democracias pobres y estancadas caen más."],
                 ["Crisis financieras", f"Logit, n = {E1['crisis']['n']:,}".replace(",", " "),
                  f"tasa real EE. UU. +{f2(cr['tasa_real_eeuu'])}; contagio +{f2(cr['contagio'])}; crecimiento {f2(cr['g'])}",
                  "Las crisis vienen de fuera: tasas de EE. UU. y contagio."],
                 ["Dinámica de la deuda", f"MCO, n = {E1['deuda']['n']:,}".replace(",", " "),
                  f"reversión {f3(de['deuda'])}; crecimiento {f2(de['g'])}; crisis +{f3(de['crisis'])}", "Reversión lenta; el crecimiento baja la deuda."],
                 ["Nacionalizaciones", f"Logit, n = {E1['nacionalizacion']['n']:,}".replace(",", " "),
                  f"choque de precio +{f2(na['nat_shock'])}; después de 1985 {f2(na['nat_post85'])}", "Se nacionaliza tras subidas del petróleo."],
                 ["Financiamiento", f"ΔCA sobre ΔI, n = {E1['financiamiento']['n']:,}".replace(",", " "),
                  f"ΔCA/ΔI = {f2(fi['dCA_dI'])} → η = {f2(fi['eta'])}; techo de déficit {pc(fi['techo_deficit_q90'])}",
                  "El 54 % de la inversión extra se paga con ahorro propio."]],
                [3.2, 2.8, 5.6, 4.6])]
story += [P("Estos submodelos se reestiman con datos hasta cada año de corte (1970, 1980, 1990, 2000, 2010 y 2019), para que la "
            "validación no use información futura.")]
story += [H2("5.2 Etapa 2: parámetros estructurales por simulación")]
story += [P("Los 23 parámetros restantes se ajustan por <b>evolución diferencial</b>. La función de pérdida combina el error del log del "
            "PIB per cápita (país-año), la dispersión del crecimiento decenal entre países (que identifica los saltos tecnológicos), la "
            "entropía cruzada y la incidencia del conflicto por década, el error en rentas de recursos, deuda y participación de la élite, "
            "y la distancia de la cobertura de la banda p10–p90 a su 80 % nominal.")]
story += [table([["Parámetro", "Valor", "Interpretación"],
                 ["b₁ · PSI en el conflicto", f2(FR["b1"]), "Casi nulo: el PSI apenas añade información al riesgo de conflicto."],
                 ["b₃ · asabiya en el conflicto", f2(FR["b3"]), "La cohesión protege fuertemente contra el conflicto."],
                 ["b₄ · rentas de recursos en el conflicto", f2(FR["b4"]), "Maldición de los recursos: las rentas elevan el riesgo."],
                 ["θ<sub>d</sub> · intercambio desigual", f3(FR["theta_d"]), "Escala del drenaje por brecha de precios."],
                 ["φ<sub>h</sub> · capacidad de absorción", f2(FR["phi_h"]), "La difusión depende mucho del capital humano relativo."],
                 ["κ<sub>m</sub>, κ<sub>f</sub> · difusión por importaciones e IED", f"{f3(FR['kappa_m'])}; {f3(FR['kappa_f'])}", "Canales de aprendizaje desde el centro."],
                 ["λ<sub>0</sub>, j<sub>0</sub> · saltos tecnológicos", f"{f3(FR['lam0'])}; {f3(FR['j0'])}", "Saltos poco frecuentes pero grandes."],
                 ["χ · costo de ajuste del capital", f2(FR["chi_k"]), "Alto: invertir mucho por encima de lo normal rinde poco."],
                 ["aid_eff · efecto de la ayuda", f3(FR["aid_eff"]), "Efecto positivo con rendimientos decrecientes."]],
                [5.4, 1.8, 9.0])]
story += [P(f"<b>Ajuste en muestra.</b> El error cuadrático medio del log del PIB per cápita es {f3(fit['rmse'])} (≈ 50 % en niveles), la "
            f"dispersión simulada del crecimiento decenal es {f3(fit['sd_sim'])} frente a {f3(fit['sd_obs'])} en los datos, y la banda p10–p90 "
            f"contiene el {pc(fit['cobertura_80'])} de las observaciones (debería contener el 80 %). El error en deuda/PIB es {f3(fit['debt_rmse'])} y "
            f"en la participación del 10 % más rico, {f3(fit['elite_rmse'])}.")]
story += [fig("f02_trayectorias", "Figura 2. PIB per cápita de ocho países. Negro: datos. Azul: el modelo reproduciendo 70 años con las "
                                  "acciones observadas, sin reanclarse a los datos. Naranja: pronóstico desde 1990 con parámetros y regla de "
                                  "decisión estimados solo con datos hasta 1990 (banda p10–p90). Rosa: proyección 2020–2030.")]
story += [P("La figura muestra la principal debilidad en muestra: simulando 70 años sin reanclarse, el modelo no reproduce los "
            "milagros de crecimiento (Corea, China) ni el despegue temprano de Brasil y México; subestima su crecimiento. En cambio, cuando "
            "se reancla al estado observado en 1990 y pronostica hacia adelante, sigue razonablemente las trayectorias de Corea, México, "
            "Brasil o Rusia, aunque subestima a India y China.")]

# ----------------------------------------------------------------------------- 6. inverse
story += [H1("6. El problema inverso: cómo deciden los países")]
story += [P("Un modelo de agentes necesita una teoría de cómo deciden los agentes. En vez de suponer que optimizan un objetivo elegido "
            "por el modelador, se infiere de los datos en dos pasos: primero, <b>qué hacen</b> (su regla de decisión); después, <b>qué "
            "parecen querer</b> (la recompensa que hace esa conducta mejor que sus alternativas). Es un problema inverso: de las acciones "
            "observadas se deducen las preferencias.")]
story += [H2("6.1 Clonación de conducta: la regla observada")]
story += [P("Para cada canal se usa un indicador observado como porcentaje del PIB y se estima una regla de ajuste parcial en escala logit, "
            "con efectos fijos por país contraídos hacia cero y regularización ridge elegida por validación fuera de muestra:")]
story += [eq(r"z_{c,t} = \rho_c\,z_{c,t-1} + \beta_c\cdot\phi(s_{t-1}) + \alpha_{i} + \varepsilon_{c,t},\qquad z=\mathrm{logit}(\mathrm{gasto}/\mathrm{PIB})")]
story += [P("donde φ son rasgos del estado: ingreso relativo, centralidad, participación de la élite, conflicto, dependencia de recursos, "
            "apertura, crecimiento poblacional, democracia y deuda.")]
R = D["conducta"]["reglas"]; ER = D["conducta"]["error_relativo"]
nm = {"k": "Capital (FBKF)", "r": "I+D + educación", "m": "Importación de manufacturas", "x": "Rentas de recursos", "f": "IED saliente", "w": "Gasto social"}
story += [table([["Canal", "Persistencia ρ", "R²", "R² solo persistencia", "Error relativo a 5 años", "a 9 años"]] +
                [[nm[c], f2(R[c]["rho"]), f2(R[c]["r2"]), f2(R[c]["r2_persistencia"]), f2(ER[c]["5"]), f2(ER[c]["9"])] for c in "krmxfw"],
                [4.2, 2.3, 1.6, 3.0, 2.8, 2.3])]
story += [P("El error relativo compara la regla con suponer que el país no cambia su gasto (menor que 1 significa que la regla es mejor). "
            "La conclusión es clara: <b>la inercia domina</b>. La regla mejora a la persistencia en torno a un 5 % en capital, importaciones "
            "e I+D, no mejora en rentas ni gasto social, y solo la inversión en el exterior responde de verdad al estado (apertura, democracia, "
            "centralidad).")]
story += [H2("6.2 Recompensa revelada: el estimador de Bajari, Benkard y Levin")]
story += [P("Si la conducta observada es óptima para cierta recompensa, cualquier desviación debería rendir menos. Se supone una recompensa "
            "lineal en seis rasgos: crecimiento del consumo (bienestar), crecimiento de la cuota del ingreso mundial (poder), crecimiento "
            "del ingreso por miembro de la élite, paz (menos riesgo de conflicto), autonomía en recursos e inercia (costo de cambiar el gasto). "
            "Se simulan 25 400 desviaciones: se altera un canal de un país hacia arriba o hacia abajo desde cinco años de origen (1960–2000) y "
            "se compara el valor descontado de los rasgos con el de la conducta observada, bajo los mismos números aleatorios. Se buscan los "
            "pesos θ que hacen que la conducta observada gane en el mayor número de comparaciones:")]
story += [eq(r"V(\sigma^{obs};\theta)\ \geq\ V(\sigma';\theta)\Leftrightarrow \theta\cdot\left[\Phi(\sigma^{obs})-\Phi(\sigma')\right]\ \geq\ 0")]
story += [P("Se minimiza una pérdida bisagra suavizada sobre la esfera unitaria y se calculan intervalos por bootstrap de países. La "
            "<i>racionalidad</i> es la fracción de desviaciones que la conducta observada supera.")]
story += [fig("f05_irl", f"Figura 3. Recompensa revelada. Izquierda: pesos globales (norma 1) con intervalo del 90 % por bootstrap de "
                         f"países; la conducta observada vence al {pc(IRL['racionalidad'])} de sus desviaciones. Derecha: pesos estimados "
                         f"por separado para cada grupo.")]
alt = IRL["racionalidad_alternativas"]
story += B([f"<b>Inercia y poder.</b> La recompensa global pesa inercia 0,84 y poder relativo 0,47; el consumo entra con signo negativo "
            f"(−0,28). La conducta observada vence al {pc(IRL['racionalidad'])} de sus desviaciones. Las recompensas teóricas puras explican "
            f"{pc(alt['bienestar'])} (bienestar), {pc(alt['poder'])} (poder) y {pc(alt['elite'])} (élite), casi lo mismo que pesos al azar "
            f"({pc(alt['aleatoria_media'])}).",
            "<b>Diferencias por grupo.</b> El centro pesa sobre todo la paz (0,97); periferia y semiperiferia, el poder y la inercia. Las "
            "autocracias tienen más inercia que las democracias. Estas estimaciones por grupo son inestables (el intervalo del peso de la paz "
            "va de 0 a 0,9), así que conviene leerlas como tendencias.",
            "<b>Qué cambiarían.</b> Bajo la recompensa estimada, aumentar I+D (92 % de las desviaciones mejoran) y extracción propia (87 %), y "
            "reducir importaciones de alto valor (68 %) habría sido rentable; subir el capital rara vez lo es (8 %).",
            "<b>La selección parsimoniosa se queda solo con la inercia</b> (61 % de racionalidad): la mayor parte de lo que los países hacen se "
            "explica porque cambiar es costoso."])
story += [box("Cómo leer este resultado",
              "El 58–61 % de racionalidad deja cerca de 40 % de la conducta sin explicar. Eso es esperable si los gobiernos siguen reglas "
              "prácticas, enfrentan restricciones externas (FMI, condicionalidad, mercados) o persiguen objetivos que el modelo no mide. "
              "La recompensa revelada describe la conducta; no dice qué deberían querer los países.")]

# ----------------------------------------------------------------------------- 7. validation
story += [PageBreak(), H1("7. Validación fuera de muestra")]
story += [H2("7.1 Diseño")]
story += [P("Se pronostica desde cada año de origen entre 1970 y 2018 (49 orígenes) a 1, 5 y 10 años. Cada origen usa solo información "
            "anterior: los parámetros calibrados con datos hasta el último corte previo (1970, 1980, 1990, 2000 o 2010), la regla de decisión "
            "estimada hasta ese año, y submodelos reestimados. En el origen el estado se reancla a los datos; después todo lo institucional, "
            "financiero y climático es endógeno. Se simulan 32 mundos por origen.")]
story += [P("Métricas: para el PIB, el <b>CRPS</b> (evalúa toda la distribución pronosticada; para una referencia puntual equivale al error "
            "absoluto), el error cuadrático, la correlación entre crecimiento pronosticado y observado y la cobertura de la banda p10–p90. "
            "Para eventos (conflicto, democracia), el puntaje de Brier y el AUC. Referencias: persistencia, deriva propia y global, un AR(1) "
            "del crecimiento, una regresión panel directa, un logit histórico de conflicto y la tendencia de temperatura.")]
story += [H2("7.2 Resultados")]
gv = V["gdp"]
story += [table([["Variable", "Horizonte", "Modelo", "Mejor referencia"],
                 ["log PIB pc · CRPS", "1 año", f3(gv["1"]["completo"]["crps"]), f"{f3(gv['1']['ar1_crecimiento']['crps'])} (AR1)"],
                 ["log PIB pc · CRPS", "5 años", f"<b>{f3(gv['5']['completo']['crps'])}</b>", f"{f3(gv['5']['panel_directo']['crps'])} (panel)"],
                 ["log PIB pc · CRPS", "10 años", f"<b>{f3(gv['10']['completo']['crps'])}</b>", f"{f3(gv['10']['ar1_crecimiento']['crps'])} (AR1)"],
                 ["log PIB pc · RMSE", "1 / 5 / 10 años", " / ".join(f3(gv[h]["completo"]["rmse"]) for h in ("1", "5", "10")),
                  "<b>" + " / ".join(f3(gv[h]["ar1_crecimiento"]["rmse"]) for h in ("1", "5", "10")) + "</b> (AR1)"],
                 ["Correlación del crecimiento", "10 años", f"<b>{f2(gv['10']['completo']['corr_crecimiento'])}</b>", f"{f2(gv['10']['panel_directo']['corr_crecimiento'])} (panel)"],
                 ["Conflicto · Brier (AUC)", "5 años", f"{f3(V['conf']['5']['completo']['brier'])} ({f2(V['conf']['5']['completo']['auc'])})",
                  f"<b>{f3(V['conf']['5']['logit_historico']['brier'])} ({f2(V['conf']['5']['logit_historico']['auc'])})</b> logit histórico"],
                 ["Deuda/PIB · RMSE", "5 / 10 años", f"<b>{f2(V['debt']['5']['completo']['rmse'])} / {f2(V['debt']['10']['completo']['rmse'])}</b>",
                  f"{f2(V['debt']['5']['persistencia']['rmse'])} / {f2(V['debt']['10']['persistencia']['rmse'])} persistencia"],
                 ["Temperatura global · RMSE", "5 / 10 años", f"<b>{f3(V['temp']['5']['completo']['rmse'])} / {f3(V['temp']['10']['completo']['rmse'])} °C</b>",
                  f"{f3(V['temp']['5']['tendencia_10a']['rmse'])} / {f3(V['temp']['10']['tendencia_10a']['rmse'])} tendencia"],
                 ["Democracia · Brier (AUC)", "5 años", f"{f3(V['demo']['5']['completo']['brier'])} ({f2(V['demo']['5']['completo']['auc'])})",
                  f"{f3(V['demo']['5']['persistencia']['brier'])} ({f2(V['demo']['5']['persistencia']['auc'])}) persistencia"],
                 ["Rentas de recursos · RMSE", "10 años", f"<b>{f3(V['rr']['10']['completo']['rmse'])}</b>", f"{f3(V['rr']['10']['persistencia']['rmse'])} persistencia"]],
                [4.4, 2.8, 3.6, 5.4])]
story += [fig("f03_validacion", "Figura 4. Izquierda: CRPS del log del PIB per cápita por horizonte para el modelo y las referencias. "
                                "Derecha: cobertura de la banda p10–p90 del modelo (debería ser 80 %).")]
story += B(["<b>Distribuciones a mediano plazo: sí.</b> A 5 y 10 años el modelo es la mejor distribución pronosticada del ingreso, y a "
            "10 años ordena mejor qué países crecerán más.",
            "<b>Error puntual y corto plazo: no.</b> Un AR(1) del crecimiento tiene menor error a todos los horizontes; a 1 año el modelo "
            "añade ruido.",
            "<b>Incertidumbre subestimada.</b> Las bandas contienen el 60–70 % de los resultados en vez del 80 %.",
            "<b>Conflicto: pierde.</b> Un logit con el historial del país predice mejor el conflicto armado; el mecanismo demográfico-"
            "estructural no añade poder predictivo a esa escala.",
            "<b>Deuda y clima: gana.</b> La dinámica de deuda estimada y la respuesta de la temperatura a las emisiones acumuladas pronostican "
            "mejor que sus referencias."])
story += [H2("7.3 Qué aporta cada teoría")]
story += [P("Para medir la contribución de cada bloque se repite la validación apagándolo, con los mismos parámetros. Si el pronóstico "
            "empeora al quitarlo, el bloque aporta información.")]
story += [fig("f04_ablaciones", "Figura 5. Ablaciones. Izquierda: cuánto empeora el CRPS del PIB a 10 años al quitar cada bloque (positivo "
                                "= el bloque ayuda). Derecha: cuánto cae el AUC de conflicto a 10 años.")]
story += [P("Deuda y crisis, instituciones y clima son los bloques que más ayudan a pronosticar el ingreso a 10 años; la regla de "
            "decisión estimada también supera a congelar las políticas. La frontera metaétnica es el bloque que más mejora la predicción de "
            "conflicto (el AUC cae 3 puntos sin ella). El sistema-mundo no mejora el pronóstico del ingreso y la demografía estructural "
            "apenas lo hace. Esto no refuta esas teorías: significa que, tal como están formuladas aquí y a horizontes de hasta 10 años, sus "
            "mecanismos no añaden información a la que ya contiene el estado observado del país.")]

# ----------------------------------------------------------------------------- 8. RL
story += [H1("8. Políticas óptimas por aprendizaje por refuerzo")]
story += [H2("8.1 Formulación")]
story += [P("Todos los países comparten una misma red neuronal de política (parámetros compartidos), pero cada uno la evalúa con su propio "
            "estado (22 rasgos: ingreso relativo, centralidad, élites, PSI, asabiya, conflicto, rentas, capital, reservas, deuda, democracia, "
            "precio de los recursos, entre otros). Cada cinco años la política elige cuánto gastar (entre 10 % y 60 % del PIB) y cómo repartirlo "
            "entre los seis canales. Se entrena con PPO (optimización proximal de políticas) durante 250 iteraciones sobre 1950–2019, con "
            "cuatro recompensas: <b>bienestar</b> (crecimiento del consumo per cápita menos años de conflicto), <b>poder</b> (crecimiento de la "
            "cuota del ingreso mundial, un juego de suma cero), <b>élite</b> (crecimiento del ingreso por miembro de la élite) y la "
            "<b>recompensa revelada</b> de la sección 6.")]
story += [H2("8.2 Resultados")]
story += [fig("f06_asignacion", "Figura 6. Reparto del gasto por zona: datos observados (proxies como % del PIB), modelo con las acciones "
                                "observadas (en unidades del modelo) y las cuatro políticas aprendidas.")]
rl = S["rl"]
story += [table([["Indicador (1990–2019 / 2019)", "Modelo histórico", "RL bienestar", "RL poder", "RL élite", "RL revelada"],
                 ["Gasto medio (% PIB)", pc(S["modelo_hist"]["presupuesto_medio"])] + [pc(rl[m]["presupuesto_medio"]) for m in ("bienestar", "poder", "elite", "irl")],
                 ["PIB pc mundial 2019 (USD)", f"{S['modelo_hist']['pib_pc_mundial_2019']:,.0f}".replace(",", " ")] +
                 [f"{rl[m]['pib_pc_mundial_2019']:,.0f}".replace(",", " ") for m in ("bienestar", "poder", "elite", "irl")],
                 ["Deuda mediana 2019", pc(S["modelo_hist"]["deuda_mediana_2019"])] + [pc(rl[m]["deuda_mediana_2019"]) for m in ("bienestar", "poder", "elite", "irl")],
                 ["Conflicto medio 1990–2019", pc1(S["modelo_hist"]["conflicto_1990_2019"])] + [pc1(rl[m]["conflicto_1990_2019"]) for m in ("bienestar", "poder", "elite", "irl")],
                 ["Reservas restantes 2019", pc(S["modelo_hist"]["reservas_restantes_2019"])] + [pc(rl[m]["reservas_restantes_2019"]) for m in ("bienestar", "poder", "elite", "irl")],
                 ["Gini entre países 2019", f2(S["modelo_hist"]["gini_2019"])] + [f2(rl[m]["gini_2019"]) for m in ("bienestar", "poder", "elite", "irl")]],
                [4.6, 2.4, 2.3, 2.3, 2.3, 2.3])]
story += B(["<b>Sin financiamiento</b> (primera versión), las cuatro políticas llevaban el 90 % o más del gasto al capital: optimizar sin "
            "costo de gastar produce soluciones de esquina que ningún país aplica.",
            "<b>Con ahorro, crédito y costos de ajuste</b>, las políticas se diferencian. Bienestar gasta menos que la historia simulada y se "
            "vuelve acreedor neto (la deuda mediana pasa a ser negativa, es decir, activos externos). Poder gasta el 46 % del PIB, se endeuda "
            "y alcanza el mayor PIB mundial. Élite destina un quinto del gasto a redistribuir: repartir frena la sobreproducción de élites y "
            "sube el ingreso por miembro, el pacto de los Estados rentistas.",
            "<b>La recompensa revelada</b> produce una política parecida a la de poder: mucho capital, deuda y agotamiento acelerado de "
            "recursos (solo queda el 4 % de las reservas en 2019).",
            "Ninguna política cambia mucho el conflicto (11–12 %): en el modelo, el riesgo depende sobre todo del ingreso, las rentas y la "
            "cohesión, que las políticas mueven poco en 30 años."])

# ----------------------------------------------------------------------------- 9. recommendations
story += [H1("9. Recomendaciones incrementales")]
story += [H2("9.1 Método")]
story += [P("Las políticas óptimas de la sección 8 se alejan tanto de la conducta real que caen fuera de la región donde el modelo fue "
            "validado. Para producir recomendaciones más creíbles se entrena una política <b>anclada</b>: cada país parte de lo que haría "
            "según su regla estimada y solo puede ajustarla dentro de un rango acotado, con un costo por alejarse (una región de confianza):")]
story += [eq(r"a_c = a_c^{\,regla}\,e^{\delta_c},\qquad \delta_c = 0.5\,\tanh(z_c),\qquad r_t = u_t - u_t^{\,regla} - \lambda\sum_c \delta_c^2")]
story += [P("El entrenamiento se hace en modo pronóstico desde cinco orígenes (1980, 1990, 2000, 2010 y 2019), con episodios de hasta 20 años "
            "en los que golpes, crisis, deuda y clima son endógenos. La recompensa se mide siempre frente a la regla sola bajo los mismos "
            "números aleatorios, y al final del episodio se valora el patrimonio neto (capital menos deuda) para que endeudarse para consumir "
            "no salga gratis. Se reportan, por país, el cambio recomendado por canal, su efecto en consumo, PIB, deuda y conflicto, la "
            "probabilidad de mejora entre mundos simulados y la robustez del signo con parámetros calibrados con datos hasta 2000, 2010 y 2019.")]
story += [H2("9.2 Resultados con objetivo de bienestar")]
G = REC["bienestar"]["global_"]
story += [fig("f07_recomendaciones", "Figura 7. Izquierda: cambio medio recomendado por canal y zona para 2020–2024, en puntos del PIB frente a "
                                     "la regla. Derecha: la misma política aplicada desde 2000 durante 20 años; diferencia de consumo y PIB per "
                                     "cápita frente a la regla.")]
story += B([f"<b>Qué recomienda.</b> Recortar el gasto unos 10 puntos del PIB (mediana), sobre todo en capital (−7) e importaciones de alto "
            f"valor (−2,8), en las tres zonas.",
            f"<b>Efecto.</b> El consumo per cápita sube en promedio un {pc1(G['d_consumo_mundial'])} durante 2020–2030 (mediana por país: 5,9 %); el PIB per cápita es un "
            f"{pc1(-G['d_pib_mundial_10a'])} menor a 10 años y la deuda baja {abs(G['d_deuda_10a']) * 100:.0f} puntos porque parte del ahorro "
            f"liberado sale al exterior. El conflicto no cambia.",
            "<b>Robustez.</b> El signo del cambio de gasto es el mismo con los tres conjuntos de parámetros en 176 de 180 países, y la "
            "probabilidad de mejorar el consumo supera el 97 % en casi todos.",
            "<b>Largo plazo.</b> Aplicada desde 2000, la ganancia de consumo baja de +6,7 % a +3,4 % en 20 años mientras el PIB cae un 8 %. "
            "Es un adelanto de consumo a costa de crecimiento futuro, que con más años probablemente se revierte."])
story += [H2("9.3 Con la recompensa revelada")]
story += [P("Con el mismo ancla y la recompensa revelada (poder relativo con peso negativo en el consumo), la política hace lo contrario: "
            "invierte unos 19 puntos más, se endeuda y recorta el consumo casi un 30 % para ganar cuota del ingreso mundial. Es una "
            "confirmación de que la recompensa revelada describe la conducta, pero no sirve como objetivo normativo.")]
story += [box("Por qué no usar estas recomendaciones todavía",
              "La recomendación de invertir menos depende de un parámetro: el costo de ajuste del capital, que la calibración fija en "
              "χ = 12. Con ese valor se pierde en promedio el 27 % de la inversión histórica, más de lo que sugiere la evidencia directa. "
              "Si la inversión rinde menos de lo que realmente rinde, el modelo naturalmente recomienda invertir menos. Antes de interpretar "
              "estas salidas como consejo hay que contrastar χ con estimaciones externas del retorno de la inversión, darle al consumo un "
              "peso político explícito (los recortes provocan protestas, según Ponticelli y Voth 2020) y extender el horizonte.")]

# ----------------------------------------------------------------------------- 10. climate & conflict
story += [H1("10. Clima, ecología y conflicto")]
story += [fig("f08_clima", "Figura 8. Izquierda: temperatura global observada, pronóstico desde 1990 (sin usar datos posteriores) y proyección "
                           "2020–2030. Derecha: emisiones fósiles observadas y pronosticadas desde 1990.")]
story += [P("El pronóstico desde 1990 reproduce bien la temperatura de 2019 aunque subestima las emisiones de ese año (28 frente a 37 Gt) "
            "porque no anticipa el auge del carbón en Asia después de 2002. El acierto en temperatura es en parte afortunado: la respuesta a "
            "las emisiones acumuladas es lenta y la diferencia de emisiones se concentra en los últimos años.")]
story += B(["<b>Responsabilidad desigual.</b> El 20 % más rico de los países (14 % de la población) acumula el 54 % del CO₂ emitido y además "
            "importa 1,6–1,9 Gt de CO₂ incorporado en el comercio; la periferia genera el 95 % de las emisiones por cambio de uso del suelo.",
            "<b>Daño no lineal.</b> La curva de Burke–Hsiang–Miguel se replica con sus datos (óptimo en 13,1 °C); en el panel PWT 1951–2019 tiene "
            "la misma forma con la mitad de magnitud (óptimo en 12,5 °C). El estudio de Kotz, Levermann y Wenz (2024) fue retractado en 2025 y "
            "no se usa.",
            "<b>Conflicto y temperatura.</b> El efecto directo de la temperatura sobre el conflicto es pequeño y no significativo; el canal "
            "principal es indirecto, por el ingreso y la capacidad estatal.",
            "<b>Límites planetarios.</b> La huella ecológica mundial pasó de 0,72 a 1,74 veces la biocapacidad entre 1961 y 2019, y el Índice "
            "Planeta Vivo cayó 69 % entre 1970 y 2018."])
story += [fig("f09_conflictos", "Figura 9. Izquierda: muertes anuales en eventos de violencia organizada (UCDP GED); el pico de 1994 es el "
                                "genocidio de Ruanda. Derecha: países con conflicto armado activo (rojo) y número de conflictos esperado por el "
                                "modelo con acciones observadas (azul).")]
story += [P("El modelo reproduce la tendencia de largo plazo del número de conflictos (de unos 3 en 1950 a unos 20 desde 1980), pero no el "
            "pico de fin de la Guerra Fría ni su caída posterior: los ciclos de conflicto responden a choques geopolíticos que el modelo no "
            "representa.")]

# ----------------------------------------------------------------------------- 11. projection
p30 = S["proyeccion_2030"]
story += [H1("11. Proyección a 2030")]
story += [P("Con los parámetros calibrados con todos los datos, las reglas de decisión estimadas y todo lo institucional, financiero y "
            "climático endógeno (salvo la población, de ONU WPP), la proyección media para 2030 es:")]
story += [table([["Indicador", "Valor"],
                 ["Crecimiento del PIB per cápita mundial", f"{p30['crecimiento_pib_pc_mundial_anual'] * 100:.1f} % anual".replace(".", ",")],
                 ["Temperatura global", f"{p30['temperatura_global_2030']:.2f} °C sobre el preindustrial".replace(".", ",")],
                 ["Proporción de democracias", pc(p30["democracias_2030"])],
                 ["Deuda pública mediana", f"{pc(p30['deuda_mediana_2030'])} del PIB"],
                 ["Probabilidad media de conflicto armado", pc(p30["prob_conflicto_media_2030"])],
                 ["Países en crisis financiera por año (2020–2030)", pc1(p30["crisis_anuales_2020_2030"])]], [9, 7.2])]
story += [P("Estas cifras son distribuciones centrales, no predicciones puntuales; dado que las bandas del modelo son demasiado estrechas, "
            "la incertidumbre real es mayor que la que muestra el dashboard.")]

# ----------------------------------------------------------------------------- 12. visualization
story += [H1("12. Visualización y capas OSINT")]
story += [P("Los resultados se exploran en un dashboard interactivo con un globo 3D (globe.gl). El globo colorea cada país por el indicador "
            "y el escenario elegidos, año por año de 1950 a 2030, y superpone capas de inteligencia de fuentes abiertas: eventos de conflicto "
            "geolocalizados de UCDP GED (1989–2023), rutas marítimas derivadas de AIS, comercio bilateral, la red mundial de rutas aéreas, "
            "centrales eléctricas, ductos, terminales de GNL, yacimientos, reactores nuevos, cables submarinos y puertos. Incluye secciones "
            "sobre el problema inverso, la validación, las políticas aprendidas, las recomendaciones por país y el clima.")]
story += [P("El visor de artifacts no puede conectarse a fuentes en tiempo real, así que ahí las capas son instantáneas. La versión con datos "
            "en vivo está integrada en el proyecto Quasarbroker (rama <font face='Mono' size='8.5'>claude/world-systems-agent-model-p0omqe</font>): "
            "un módulo SISTEMA-MUNDO con API propia, las capas nuevas en el mapa MapLibre y un selector entre mapa 2D y globo 3D que también "
            "muestra vuelos, barcos y sismos en vivo.")]

# ----------------------------------------------------------------------------- 13. conclusions
story += [H1("13. Conclusiones")]
story += [H2("13.1 Sobre las teorías")]
story += B(["<b>La inercia gobierna las decisiones de los países.</b> Tanto la regla estimada como la recompensa revelada indican que "
            "cambiar la composición del gasto es costoso; explicar la conducta exige incluir ese costo.",
            "<b>Los países parecen buscar poder relativo más que bienestar.</b> La recompensa revelada pesa la cuota del ingreso mundial y no "
            "el consumo; esto es coherente con la visión realista de la competencia entre Estados y con la del sistema-mundo, en la que la "
            "posición relativa es lo que se disputa. El centro se distingue por valorar la paz.",
            "<b>Deuda, crisis e instituciones sí predicen.</b> Son los mecanismos que más mejoran el pronóstico del ingreso a 10 años, y las "
            "crisis se explican sobre todo por choques externos (tasas de EE. UU. y contagio).",
            "<b>La cohesión importa para el conflicto.</b> La frontera metaétnica (asabiya) es el bloque que más aporta a predecir el conflicto, "
            "y la asabiya es el factor protector más fuerte en el logit calibrado; las rentas de recursos, el de mayor riesgo.",
            "<b>El PSI, tal como se formuló, no añade poder predictivo.</b> Su coeficiente calibrado es casi nulo. Puede que el índice necesite "
            "otra medición (por ejemplo, datos directos de competencia intraélite) o que actúe en horizontes más largos que los validados.",
            "<b>Los flujos del sistema-mundo no mejoran el pronóstico a 10 años.</b> El drenaje existe en los datos y ayuda a explicar la "
            "distribución de rentas, pero su efecto sobre el crecimiento de mediano plazo ya está contenido en el estado observado."])
story += [H2("13.2 Sobre el modelo como herramienta")]
story += B(["<b>Sirve para pronosticar distribuciones a mediano plazo</b> (5–10 años) del ingreso, la deuda y la temperatura mejor que "
            "referencias estadísticas estándar, y para explorar mecanismos.",
            "<b>No sirve para pronósticos de corto plazo ni de conflicto</b>, donde modelos estadísticos simples ganan.",
            "<b>Subestima la incertidumbre</b>: las bandas deberían ser más anchas.",
            "<b>No reproduce los milagros de crecimiento</b> cuando se simula largo tiempo sin reanclarse a los datos.",
            "<b>Todavía no es una herramienta de recomendación.</b> Las políticas óptimas son extremas y las recomendaciones ancladas dependen de "
            "un parámetro (el costo de ajuste) que parece mal identificado."])

# ----------------------------------------------------------------------------- 14. limits
story += [H1("14. Limitaciones y trabajo futuro")]
story += [table([["Limitación", "Consecuencia", "Siguiente paso"],
                 ["Costo de ajuste alto (χ = 12)", "Recomienda invertir menos", "Contrastar con retornos de la inversión; prior externo"],
                 ["Bandas demasiado estrechas", "Incertidumbre subestimada", "Calibración bayesiana; conjuntos de modelos"],
                 ["Un solo recurso genérico", "Sin ciclos del petróleo ni sustitución", "Separar petróleo, gas, minerales; descubrimientos"],
                 ["Población y capital humano exógenos", "Sin retroalimentación demográfica", "Fecundidad y educación endógenas"],
                 ["El consumo no tiene peso político", "Los recortes no generan protesta", "Estimar el vínculo austeridad–protesta"],
                 ["Recompensa lineal en 6 rasgos", "40 % de la conducta sin explicar", "Rasgos adicionales; restricciones externas"],
                 ["RL con parámetros compartidos", "Sin equilibrio garantizado", "Juegos multiagente; mejores respuestas por país"],
                 ["Datos parcialmente de copias públicas", "Posibles diferencias de versión", "Reemplazar por fuentes oficiales"]],
                [4.6, 4.8, 6.8])]

# ----------------------------------------------------------------------------- appendix
story += [PageBreak(), H1("Apéndice A. Reproducción")]
story += [P("Todo el trabajo es reproducible desde el repositorio. Los pasos, en orden:")]
cmds = ["python src/fetch_data.py && python src/data_prep.py", "python -m sources.<bloque> (acciones, elites, finanzas, comercio, recursos, geopolitica, demografia, clima)",
        "python src/merge_sources.py", "python src/calibrate.py (calibración final)", "validate.run_rolling_calibration() (cortes 1970–2010)",
        "python src/irl.py (reglas y recompensa revelada)", "python src/validate.py (validación)", "python src/rl.py (PPO, cuatro recompensas)",
        "python src/recommend.py (recomendaciones ancladas)", "python src/osint.py (capas OSINT)", "python src/analyze.py && python src/build_dashboard.py",
        "python reports/figures.py && python reports/build_report.py (este informe)"]
story += [Paragraph(c, ParagraphStyle("c", fontName="Mono", fontSize=8, leading=11, textColor=INK, leftIndent=10), bulletText="›") for c in cmds]
story += [Spacer(1, 8), H1("Apéndice B. Glosario")]
story += [table([["Término", "Significado"],
                 ["Asabiya", "Capacidad de un grupo para actuar colectivamente (Ibn Jaldún, Turchin)."],
                 ["BBL", "Estimador de Bajari, Benkard y Levin (2007): infiere preferencias exigiendo que la conducta observada supere a sus desviaciones."],
                 ["Clonación de conducta", "Estimar de los datos la regla que mapea estados a acciones."],
                 ["CRPS", "Continuous Ranked Probability Score: mide la calidad de una distribución pronosticada; menor es mejor."],
                 ["EMP, MMP, SFD, PSI", "Potencial de movilización de élites y de masas, angustia fiscal del Estado, e índice de estrés político."],
                 ["Evolución diferencial", "Algoritmo de optimización global basado en poblaciones de soluciones candidatas."],
                 ["Intercambio desigual", "Transferencia de valor por comercio entre países con salarios y precios muy distintos (Emmanuel)."],
                 ["Números aleatorios comunes", "Usar los mismos sorteos al comparar simulaciones, para aislar el efecto de una decisión."],
                 ["PPO", "Proximal Policy Optimization: algoritmo de aprendizaje por refuerzo con actualizaciones acotadas."],
                 ["TCRE", "Respuesta climática transitoria a las emisiones acumuladas de CO₂."]], [4.0, 12.2])]
story += [Spacer(1, 8), H1("Apéndice C. Referencias principales")]
refs = ["Acemoglu, D., Naidu, S., Restrepo, P. y Robinson, J. (2019). Democracy does cause growth. <i>Journal of Political Economy</i> 127(1).",
        "Amin, S. (1974). <i>Accumulation on a World Scale</i>. Monthly Review Press.",
        "Bajari, P., Benkard, C. L. y Levin, J. (2007). Estimating dynamic models of imperfect competition. <i>Econometrica</i> 75(5).",
        "Burke, M., Hsiang, S. y Miguel, E. (2015). Global non-linear effect of temperature on economic production. <i>Nature</i> 527.",
        "Coe, D. y Helpman, E. (1995). International R&amp;D spillovers. <i>European Economic Review</i> 39(5).",
        "Collier, P. y Hoeffler, A. (2004). Greed and grievance in civil war. <i>Oxford Economic Papers</i> 56(4).",
        "Emmanuel, A. (1972). <i>Unequal Exchange</i>. Monthly Review Press.",
        "Feenstra, R., Inklaar, R. y Timmer, M. (2015). The next generation of the Penn World Table. <i>AER</i> 105(10).",
        "Feldstein, M. y Horioka, C. (1980). Domestic saving and international capital flows. <i>Economic Journal</i> 90.",
        "Goldstone, J. (1991). <i>Revolution and Rebellion in the Early Modern World</i>. University of California Press.",
        "Guriev, S., Kolotilin, A. y Sonin, K. (2011). Determinants of nationalization in the oil sector. <i>JLEO</i> 27(2).",
        "Hayashi, F. (1982). Tobin's marginal q and average q. <i>Econometrica</i> 50(1).",
        "Hickel, J., Dorninger, C., Wieland, H. y Suwandi, I. (2022). Imperialist appropriation in the world economy. <i>Global Environmental Change</i> 73.",
        "Laeven, L. y Valencia, F. (2020). Systemic banking crises database II. <i>IMF Economic Review</i> 68.",
        "Powell, J. y Thyne, C. (2011). Global instances of coups from 1950 to 2010. <i>Journal of Peace Research</i> 48(2).",
        "Reinhart, C., Rogoff, K. y Savastano, M. (2003). Debt intolerance. <i>Brookings Papers on Economic Activity</i>.",
        "Schulman, J. et al. (2017). Proximal policy optimization algorithms. arXiv:1707.06347.",
        "Sundberg, R. y Melander, E. (2013). Introducing the UCDP Georeferenced Event Dataset. <i>Journal of Peace Research</i> 50(4).",
        "Turchin, P. (2003). <i>Historical Dynamics</i>. Princeton University Press.",
        "Turchin, P. y Nefedov, S. (2009). <i>Secular Cycles</i>. Princeton University Press.",
        "Turchin, P. (2016). <i>Ages of Discord</i>. Beresta Books.",
        "Wallerstein, I. (1974). <i>The Modern World-System I</i>. Academic Press."]
story += [Paragraph(r, ParagraphStyle("r", fontName="Serif", fontSize=9, leading=12, leftIndent=12, firstLineIndent=-12, textColor=INK, spaceAfter=3)) for r in refs]


if __name__ == "__main__":
    doc = Doc(str(OUT))
    doc.multiBuild(story)
    print(OUT, round(OUT.stat().st_size / 1e6, 2), "MB")
