"""Build the single-file Lab 6 submission from recorded evidence."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import subprocess
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / 'LAB6'
OUT = ROOT / 'output/pdf/Lab_6_Bike_Share_Coverage_Report.pdf'
TMP = ROOT / 'tmp/pdfs'
OUT.parent.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
BLACK = HexColor('#000000')
GRAY = HexColor('#444444')
LIGHT = HexColor('#eeeeee')
STYLE = ParagraphStyle('body', fontName='Helvetica', fontSize=10.3,
                       leading=15.4, textColor=BLACK)
SMALL = ParagraphStyle('small', parent=STYLE, fontSize=8.8, leading=12.5)
c = canvas.Canvas(str(TMP/'report_body.pdf'), pagesize=A4)
c.setTitle('Lab 6 - Bike Share Rental: Code and Branch Coverage')
c.setAuthor('Bhavesh V')
page = 0
W, H = A4
Y = 0

def start(title, sub='', wide=False):
    global W, H, Y, page
    if page:
        c.showPage()
    page += 1
    W, H = landscape(A4) if wide else A4
    c.setPageSize((W,H))
    c.setFillColor(BLACK)
    c.rect(0,H-10,W,10,fill=1,stroke=0)
    c.setFillColor(GRAY)
    c.setFont('Helvetica',8)
    c.drawString(42,H-33,'SOFTWARE TESTING  /  LAB 6  /  BIKE SHARE RENTAL')
    c.setFillColor(BLACK)
    c.setFont('Helvetica-Bold',21 if not wide else 19)
    c.drawString(42,H-68,title)
    Y=H-89
    if sub:
        p(sub,small=True)
    c.setStrokeColor(HexColor('#cccccc'))
    c.line(42,37,W-42,37)
    c.setFillColor(GRAY)
    c.setFont('Helvetica',8)
    c.drawString(42,24,'Bhavesh V  |  PES1UG24CS115  |  Section B  |  03 November 2026')
    c.drawRightString(W-42,24,str(page))

def p(text, small=False, after=9):
    global Y
    para=Paragraph(text, SMALL if small else STYLE)
    _,h=para.wrap(W-84,1000)
    assert Y-h>45, (page,text[:60],Y,h)
    para.drawOn(c,42,Y-h)
    Y-=h+after

def h(text):
    global Y
    Y-=5
    c.setFillColor(BLACK)
    c.setFont('Helvetica-Bold',12)
    c.drawString(42,Y-12,text)
    Y-=25

def table(rows,widths):
    global Y
    data=[[Paragraph(escape(str(x)),SMALL) for x in row] for row in rows]
    t=Table(data,colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),LIGHT),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,0),(-1,-1),0.4,HexColor('#dddddd')),
    ]))
    _,height=t.wrap(W-84,1000)
    assert Y-height>45,(page,Y,height)
    t.drawOn(c,42,Y-height)
    Y-=height+12

def code_file(filename, first=1, last=None, title=None):
    global Y
    lines=(LAB/filename).read_text().splitlines()
    last=last or len(lines)
    start(title or filename,
          f'Complete maintained source listing, lines {first}-{last}. '
          'Numbers at left are report annotations, not part of the file.')
    Y-=3
    size=8.05
    leading=9.45
    for n in range(first,last+1):
        line=lines[n-1]
        # Courier is deterministic and preserves every source character.
        assert c.stringWidth(line,'Courier',size)<W-111,(filename,n,line)
        assert Y-leading>45,(filename,n,Y)
        c.setFillColor(GRAY);c.setFont('Courier',7)
        c.drawRightString(63,Y-8,str(n))
        c.setFillColor(BLACK);c.setFont('Courier',size)
        c.drawString(74,Y-8,line)
        Y-=leading

def screenshot(name, bottom=None, width=None, crop=None):
    global Y
    im=Image.open(LAB/'evidence'/name).convert('L')
    if crop:
        im=im.crop(crop)
    elif bottom:
        im=im.crop((0,0,im.width,bottom))
    draw_w=width or W-84
    draw_h=draw_w*im.height/im.width
    assert Y-draw_h>45,(page,Y,draw_h)
    c.drawImage(ImageReader(im),42,Y-draw_h,width=draw_w,height=draw_h)
    Y-=draw_h+10

branch=json.loads((LAB/'evidence/branch.json').read_text())
assert branch['totals']['covered_lines']==40
assert branch['totals']['covered_branches']==30

start('Code and branch coverage analysis',
      'L6_L7_53_bike_share_rental / Python application: bike_share_rental.py')
p('<b>Student:</b> Bhavesh V &nbsp;&nbsp; <b>SRN:</b> PES1UG24CS115 &nbsp;&nbsp; <b>Section:</b> B')
h('Final result')
table([
    ['Measure','Recorded result','Target'],
    ['Line coverage','40 / 40 executable statements = 100%','At least 90%'],
    ['Branch coverage','30 / 30 measured outcomes = 100%','At least 90%'],
    ['Final test suite','57 passed; 0 failed','All assertions pass'],
    ['Missing / partial','0 missing statements; 0 partial branches','No uncovered measured outcomes'],
], [122,285,104])
p('The original application is unchanged. Coverage is restricted to the application '
  'module, so executing test code does not inflate the reported percentages. '
  'No source lines or branches are excluded.')
h('Initial measurement and improvement')
p('The two starter tests passed but executed only 20 of 40 statements '
  '(<b>50.00% line coverage</b>) and 11 of 30 branch outcomes '
  '(<b>36.67% branch coverage</b>). The initial branch-mode terminal report '
  'displayed <b>44%</b>: its Cover column combines statements and branches, '
  '(20 + 11) / (40 + 30) = 44.29%, rounded for display.')
p('Stage 1 adds a maintained suite of 17 cases and reaches 100% line coverage. '
  'Stage 2 retains those cases and adds 40 decision and boundary cases. '
  'The final standalone branch suite passes 57 cases and reaches 100% on both measures.')
h('Coverage concepts')
p('<b>Line coverage</b> measures executed statements. <b>Branch coverage</b> '
  'measures alternative control-flow destinations. <b>Function coverage</b> '
  'asks whether each function was invoked; all three application functions were invoked. '
  '<b>Path coverage</b> considers complete routes through the program and is not '
  'established by these reports. Full measured coverage does not prove correctness.')

start('Test design and coverage reasoning')
p('Tests use fixed expected prices, status strings, exception messages and boolean '
  'results. Parametrization keeps individual input combinations independently visible '
  'to pytest; the final suite contains 57 collected cases.')
table([
 ['Area','Inputs and asserted behavior'],
 ['Ride prices', 'All three rates; 1, 29, 30, 31, 60 and 61 minutes test block rounding. '
  'A 30-minute standard ride costs 20; 31 minutes costs 40.'],
 ['Subscription and peak', 'First block is free. A subscriber ride up to 30 minutes '
  'returns 0 even at peak. Cargo is exempt from peak surcharge; standard adds 15.'],
 ['Long rides', '180 minutes does not add the long-ride fee; 181 does. Standard '
  'non-subscriber prices are 120 and 240. An electric subscriber peak ride at 181 '
  'minutes costs 6 x 35 + 15 + 100 = 325.'],
 ['Validation', 'Unknown bike; zero/negative minutes; zero/negative capacity; '
  'negative bike count and bike count above capacity each raise ValueError.'],
 ['Dock decisions', 'All five statuses; 0/full and 1/2/3 bike boundaries; '
  '1/2/3 free-slot boundaries. Empty/full take precedence at capacity 1. '
  'With 1 bike and capacity 3, few bikes takes precedence over few slots.'],
 ['Unlock decisions', 'Active rides deny unlocking. Ages 15, 16, 17 and 18; '
  'teen balances 99/100 and adult balances 49/50. Both passing and failing '
  'balance comparisons are asserted, including a negative adult balance.'],
], [118,393])
h('Measured branches by function')
table([
 ['Function','Statements covered','Branch outcomes covered'],
 ['ride_cost','15 / 15','12 / 12'],
 ['dock_status','14 / 14','12 / 12'],
 ['can_unlock','7 / 7','6 / 6'],
 ['Module-level statements','4 / 4','0 (no decisions)'],
], [171,170,170])
p('Coverage.py measures line-to-line branches. Boolean return comparisons and '
  'short-circuit operands may not produce separate measured arcs. The explicit '
  'threshold and compound-condition cases strengthen behavior checks beyond the '
  'coverage total; this is not a claim of exhaustive condition or path coverage.',small=True)

start('Execution, evidence and repository history')
h('Environment and reproduction')
p('Executed on 03 November 2026 (Asia/Kolkata): Python 3.12.13, pytest 9.2.0, '
  'coverage.py 7.17.0. Test dependencies are pinned in LAB6/requirements.txt.')
commands='''python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r LAB6/requirements.txt
python LAB6/run_coverage.py line
python LAB6/run_coverage.py branch
python -m pytest -q'''
for line in commands.splitlines():
    p('<font name="Courier" size="8.6">'+escape(line)+'</font>',after=3)
p('Run from the repository root. The runner switches to LAB6, runs the named '
  'test file explicitly and uses independent COVERAGE_FILE databases. It saves '
  'stdout, JSON, and HTML reports. The final ordinary pytest command also '
  'collected and passed all 57 cases.',after=8)
h('Two implementation commits completed')
table([
 ['Commit','Change'],
 ['856e691','Complete line coverage tests with 100 percent coverage and evidence'],
 ['9789f30','Complete branch coverage with 57 passing cases and 100 percent coverage'],
], [93,418])
p('Both are local repository commits. The line commit includes the maintained '
  'line test file and screenshot; the branch commit includes the maintained '
  'branch test file and screenshot. Existing application code is preserved.')
h('Evidence included in this single PDF')
p('The next two landscape pages contain the genuine Terminal screenshots '
  'provided by the student after running the line and branch coverage commands. '
  'Each page reproduces the complete supplied screenshot in grayscale and includes an enlarged '
  'detail of its results table for readability. Only final results above 90% '
  'are shown as screenshots.')
p('The appendices reproduce the complete application, both named test files and '
  'the default pytest entry point. Embedded PDF attachments preserve the runnable '
  'Python files, requirements, README, grayscale Terminal screenshots, saved '
  'runner stdout, JSON coverage data and the '
  'two-commit history. A PDF reader with attachment support can extract them.')
p('Source reference: Lab_6_Code&amp;BranchCoverage_Student_Handout.docx (1).pdf, '
  'especially the steps and deliverables on pages 3-4. Repository evidence and '
  'local test executions supply all result values in this report.',small=True)

start('Evidence 1 / Final line coverage',
      '17 passed. All 40 executable statements covered; no missing lines. '
      'Genuine Terminal screenshot supplied by the student, reproduced in grayscale.',wide=True)
screenshot('line_coverage.png')
h('Enlarged coverage table from the same screenshot')
screenshot('line_coverage.png',width=690,crop=(0,132,1100,274))
p('Line coverage = 40 / 40 x 100 = 100.00%. '
  'The report records 40 statements, 0 missed statements and 100% coverage. '
  'The screenshot shows 17 passed in 0.02 seconds.',small=True)

start('Evidence 2 / Final branch coverage',
      '57 passed. 40/40 statements and 30/30 measured branch outcomes covered. '
      'Genuine Terminal screenshot supplied by the student, reproduced in grayscale.',wide=True)
screenshot('branch_coverage.png')
h('Enlarged coverage table from the same screenshot')
screenshot('branch_coverage.png',width=690,crop=(0,132,1100,274))
p('BrPart = 0 and Missing is empty. The explicit branch ratio is 30 / 30 = 100.00%; '
  'the combined Cover result is also 100%. The screenshot shows 57 passed in '
  '0.04 seconds.',small=True)

code_file('bike_share_rental.py',title='Appendix A / Application under test')
p('Application source is byte-for-byte identical to the original repository version '
  '(commit 17b7c82). SHA-256: '+hashlib.sha256((LAB/'bike_share_rental.py').read_bytes()).hexdigest(),small=True)
code_file('CodeCoverageTest_53_bike_share_rental.py',title='Appendix B / Line coverage tests')
code_file('BranchCoverageTest_53_bike_share_rental.py',1,46,
          title='Appendix C / Branch tests, part 1')
p('The five imported stage-1 test functions are collected with the new branch '
  'cases, allowing this file to run independently.',small=True)
code_file('BranchCoverageTest_53_bike_share_rental.py',47,88,
          title='Appendix C / Branch tests, part 2')
h('Default pytest entry point: test_bike_share_rental.py')
for line in (LAB/'test_bike_share_rental.py').read_text().splitlines():
    c.setFillColor(BLACK);c.setFont('Courier',8.05)
    c.drawString(42,Y-8,line);Y-=10
p('Use one entry point per run. The default filename supports normal pytest '
  'discovery; explicitly collecting it together with the named deliverables '
  'would collect the imported cases more than once.',small=True)
c.save()

history=subprocess.check_output(
    ['git','log','-2','--format=%h %s','9789f30'],cwd=ROOT,text=True)
(LAB/'evidence/implementation_commits.txt').write_text(history)
writer=PdfWriter()
writer.clone_document_from_reader(PdfReader(TMP/'report_body.pdf'))
attachments=[
 'bike_share_rental.py','CodeCoverageTest_53_bike_share_rental.py',
 'BranchCoverageTest_53_bike_share_rental.py','test_bike_share_rental.py',
 'run_coverage.py','requirements.txt','README.md',
 'evidence/line_terminal.txt','evidence/branch_terminal.txt',
 'evidence/line.json','evidence/branch.json',
 'evidence/baseline/line.txt','evidence/baseline/branch.txt',
 'evidence/baseline/line.json','evidence/baseline/branch.json',
 'evidence/implementation_commits.txt',
 'evidence/line_coverage.png','evidence/branch_coverage.png',
]
for item in attachments:
    if item in ('evidence/line_coverage.png','evidence/branch_coverage.png'):
        buffer=BytesIO()
        Image.open(LAB/item).convert('L').save(buffer,format='PNG')
        data=buffer.getvalue()
    else:
        data=(LAB/item).read_bytes()
    writer.add_attachment(item.replace('/','__'),data)
with OUT.open('wb') as stream:
    writer.write(stream)
print(f'{OUT}\nPages: {page}\nSize: {OUT.stat().st_size:,} bytes')
