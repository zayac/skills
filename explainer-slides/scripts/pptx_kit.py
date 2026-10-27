"""python-pptx helpers: dark 16:9 deck, native shapes, formula images, and OOXML click animations"""
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

# ManimGL colours used in the video
BG, WHITE = "1C1C1C", "FFFFFF"
GREY_A, GREY_B, GREY_C, GREY_D = "DDDDDD", "BBBBBB", "888888", "555555"
BLUE_B, BLUE_C, YELLOW, RED, GREEN, TEAL, PINK = "9CDCEB", "58C4DD", "FFFF00", "FC6255", "83C167", "5CD0B3", "D147BD"
FONT = "STIX Two Text"  # serif close to the video's; Google's editors lack plain Noto Serif (import falls back to Arial)
MATH_FONT = "STIX Two Math"
MATH_CHARS = set("\u2208\u222a\u21d4\u21d2\u2248")  # ∈ ∪ ⇔ ⇒ ≈ set in the math font
LEFT, CENTER, RIGHT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def rgb(hex_):
    return RGBColor.from_string(hex_)


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(10), Inches(5.625)

    def slide(self, notes, transition=True):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(BG)
        slide.notes_slide.notes_text_frame.text = notes
        if transition:
            insert_in_order(slide, etree.fromstring(f'<p:transition xmlns:p="{P_NS}" spd="med"><p:fade/></p:transition>'))
        return slide

    def save(self, path):
        self.prs.save(path)


def text(slide, x, y, w, h, s, size=16, color=WHITE, bold=False, italic=False, align=LEFT, anchor=MSO_ANCHOR.MIDDLE):
    """Text box with zero padding; `s` may contain newlines (one paragraph each)"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, line in enumerate(s.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for chunk, is_math in split_math(line):
            run = p.add_run()
            run.text = chunk
            run.font.size, run.font.bold, run.font.italic = Pt(size), bold and not is_math, italic
            run.font.name = MATH_FONT if is_math else FONT
            run.font.color.rgb = rgb(color)
    return box


def split_math(line):
    """Runs of (text, is_math): symbols missing from the text font go in the math font"""
    chunks = []
    for ch in line:
        is_math = ch in MATH_CHARS
        if chunks and chunks[-1][1] == is_math:
            chunks[-1][0] += ch
        else:
            chunks.append([ch, is_math])
    return [tuple(c) for c in chunks]


def title(slide, s):
    return text(slide, 0.5, 0.3, 9, 0.6, s, size=28, bold=True)


def tag(slide, s, x=4.3, y=5.25, w=5.5, align=RIGHT, color=GREY_B):
    return text(slide, x, y, w, 0.25, s, size=11, color=color, align=align)


def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=1.5, rot=0.0, alpha=None, dash=False):
    sp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            set_alpha(sp.fill._xPr.find(qn("a:solidFill")), alpha)
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(line_w)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    sp.rotation = rot
    return sp


def set_alpha(solid_fill, alpha):
    solid_fill[0].append(etree.fromstring(f'<a:alpha xmlns:a="{A_NS}" val="{int(alpha * 100000)}"/>'))


def rect(slide, x, y, w, h, **kw):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, **kw)


def box(slide, x, y, w, h, color=YELLOW, width=2.25):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, line=color, line_w=width)


def dot(slide, cx, cy, r, color, outline=None, alpha=None):
    return shape(slide, MSO_SHAPE.OVAL, cx - r, cy - r, 2 * r, 2 * r, fill=color, line=outline, line_w=1, alpha=alpha)


def line(slide, x1, y1, x2, y2, color=GREY_B, width=1.25, arrow=False, dash=False, alpha=None):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(width)
    if alpha is not None:
        set_alpha(ln.line._get_or_add_ln().find(qn("a:solidFill")), alpha)
    if dash:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if arrow:
        ln.line._get_or_add_ln().append(etree.fromstring(f'<a:tailEnd xmlns:a="{A_NS}" type="triangle" w="med" len="med"/>'))
    return ln


def picture(slide, path, x, y, w=None, h=None, border=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), **kw)
    if border:
        pic.line.color.rgb = rgb(border)
        pic.line.width = Pt(1)
    return pic


def formula(slide, name, x, y, align=LEFT, scale=1.0):
    """Formula PNG at its natural size (rendered at 300 dpi at the slide font size); x is its left, centre or right"""
    path = f"assets/{name}.png"
    w, h = Image.open(path).size
    w, h = w / 300 * scale, h / 300 * scale
    left = {LEFT: x, CENTER: x - w / 2, RIGHT: x - w}[align]
    pic = slide.shapes.add_picture(path, Inches(left), Inches(y), Inches(w), Inches(h))
    return pic


class Plot:
    """Linear map from data coordinates to slide inches"""
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr

    def __call__(self, x, y):
        sx = self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w
        sy = self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h
        return sx, sy

    def scale(self):
        return self.w / (self.xr[1] - self.xr[0])


def insert_in_order(slide, el):
    """p:transition and p:timing go after p:clrMapOvr, transition first"""
    sld = slide._element
    transition = sld.find(qn("p:transition"))
    anchor = transition if el.tag == qn("p:timing") and transition is not None else sld.find(qn("p:clrMapOvr"))
    anchor.addnext(el)


class Timing:
    """Clicks of (shape, effect, delay_ms) triples; the first effect of a click starts on click, the rest with it"""
    def __init__(self):
        self.next_id = 3

    def tid(self):
        self.next_id += 1
        return self.next_id - 1

    def set_vis(self, spid, val, delay):
        return (f'<p:set><p:cBhvr><p:cTn id="{self.tid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{delay}"/>'
                f'</p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst>'
                f'<p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="{val}"/></p:to></p:set>')

    def anim(self, spid, attr, frm, to, dur):
        return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{self.tid()}" dur="{dur}" fill="hold"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst>'
                f'</p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
                f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')

    def fade(self, spid, direction, dur):
        return (f'<p:animEffect transition="{direction}" filter="fade"><p:cBhvr><p:cTn id="{self.tid()}" dur="{dur}"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')

    def effect(self, spid, kind, delay, node_type, dur=500):
        cid = self.tid()
        if kind == "fade_in":
            preset, cls, sub = 10, "entr", 0
            body = self.set_vis(spid, "visible", 0) + self.fade(spid, "in", dur)
        elif kind == "fade_out":
            preset, cls, sub = 10, "exit", 0
            body = self.fade(spid, "out", dur) + self.set_vis(spid, "hidden", dur - 1)
        elif kind == "fly_up":
            preset, cls, sub = 2, "entr", 4
            body = (self.set_vis(spid, "visible", 0) + self.anim(spid, "ppt_x", "#ppt_x", "#ppt_x", dur)
                    + self.anim(spid, "ppt_y", "1+#ppt_h/2", "#ppt_y", dur))
        elif kind == "fly_left":
            preset, cls, sub = 2, "entr", 8
            body = (self.set_vis(spid, "visible", 0) + self.anim(spid, "ppt_x", "0-#ppt_w/2", "#ppt_x", dur)
                    + self.anim(spid, "ppt_y", "#ppt_y", "#ppt_y", dur))
        elif kind == "zoom_in":
            preset, cls, sub = 53, "entr", 16
            body = (self.set_vis(spid, "visible", 0) + self.anim(spid, "ppt_w", "0", "#ppt_w", dur)
                    + self.anim(spid, "ppt_h", "0", "#ppt_h", dur) + self.fade(spid, "in", dur))
        else:
            raise ValueError(kind)
        return (f'<p:par><p:cTn id="{cid}" presetID="{preset}" presetClass="{cls}" presetSubtype="{sub}" fill="hold" '
                f'grpId="0" nodeType="{node_type}"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
                f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')

    def build(self, slide, clicks):
        parts = []
        for click in clicks:
            outer, inner = self.tid(), self.tid()
            effects = "".join(
                self.effect(sp.shape_id, kind, delay, "clickEffect" if i == 0 else "withEffect")
                for i, (sp, kind, delay) in enumerate(click)
            )
            parts.append(
                f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
                f'<p:childTnLst><p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst>{effects}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            )
        xml = (
            f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
            f'<p:childTnLst>{"".join(parts)}</p:childTnLst></p:cTn>'
            f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
            f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
        )
        insert_in_order(slide, etree.fromstring(xml))


def appear(shapes, kind="fade_in", delay=0, stagger=0):
    """Effects for a list of shapes, optionally staggered"""
    return [(sp, kind, delay + i * stagger) for i, sp in enumerate(shapes)]
