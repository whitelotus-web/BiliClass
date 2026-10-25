"""Compact bilingual reference vocabulary, organised by the GDPT subject list.

These short pairs are BiliClass editorial references, not an official Ministry
English dictionary, a copy of textbooks, or certification of curriculum coverage.
References support the subject terminology; they do not certify each translation.
"""

import hashlib
import unicodedata
from functools import lru_cache

from .subject_terms import subject_key
from .terminology_seed_extra import EXTRA

VERSION = '2026.10.25.2'
PACK_ID = 'biliclass-school-terminology'
CURRICULUM_URL = 'https://congbao.chinhphu.vn/van-ban/thong-tu-so-17-2025-tt-bgddt-46255.htm'

# Primary publishers and educational institutions. No downloaded textbook text.
SOURCES = {
    'math': ('OpenStax · Algebra and Trigonometry', 'OpenStax, Rice University',
             'https://openstax.org/books/algebra-and-trigonometry-2e/pages/index'),
    'physics': ('OpenStax · Physics', 'OpenStax, Rice University',
                'https://openstax.org/books/physics/pages/index'),
    'chemistry': ('OpenStax · Chemistry 2e', 'OpenStax, Rice University',
                  'https://openstax.org/books/chemistry-2e/pages/index'),
    'biology': ('OpenStax · Biology 2e', 'OpenStax, Rice University',
                'https://openstax.org/books/biology-2e/pages/index'),
    'computing': ('NIST · Computer Security Resource Center Glossary', 'NIST',
                  'https://csrc.nist.gov/glossary'),
    'technology': ('OpenStax · Physics · applications', 'OpenStax, Rice University',
                   'https://openstax.org/books/physics/pages/1-introduction'),
    'science': ('OpenStax · Biology 2e · scientific inquiry', 'OpenStax, Rice University',
                'https://openstax.org/books/biology-2e/pages/1-1-the-science-of-biology'),
    'history': ('OpenStax · World History Volume 1', 'OpenStax, Rice University',
                'https://openstax.org/books/world-history-volume-1/pages/1-introduction'),
    'geography': ('National Geographic · Geography', 'National Geographic Society',
                  'https://education.nationalgeographic.org/resource/geography-article/'),
    'literature': ('OpenStax · Writing Guide', 'OpenStax, Rice University',
                   'https://openstax.org/books/writing-guide/pages/1-5-writing-process-thinking-critically-about-a-text'),
    'language': ('British Council · English grammar', 'British Council',
                 'https://learnenglish.britishcouncil.org/grammar'),
    'music': ('Open Music Theory', 'VIVA Open Publishing',
              'https://viva.pressbooks.pub/openmusictheory/'),
    'art': ('Tate · Art terms', 'Tate', 'https://www.tate.org.uk/art/art-terms'),
    'citizenship': ('UNESCO · Global citizenship and peace education', 'UNESCO',
                    'https://www.unesco.org/en/global-citizenship-peace-education'),
    'economics': ('OpenStax · Principles of Economics 3e', 'OpenStax, Rice University',
                  'https://openstax.org/books/principles-economics-3e/pages/index'),
    'health': ('WHO · Physical activity', 'World Health Organization',
               'https://www.who.int/news-room/fact-sheets/detail/physical-activity'),
    'heritage': ('UNESCO · What is intangible cultural heritage?', 'UNESCO',
                 'https://ich.unesco.org/en/what-is-intangible-heritage-00003'),
    'career': ('ILO · Skills and lifelong learning', 'International Labour Organization',
               'https://www.ilo.org/topics-and-sectors/skills-and-lifelong-learning'),
    'peace': ('UN · Principles of peacekeeping', 'United Nations',
              'https://peacekeeping.un.org/en/principles-of-peacekeeping'),
}

# A pair is a complete term/heading. New seed nouns are exact-only: putting a
# singular noun inside every sentence would prevent normal English inflection.
GROUPS = {
    'math': ('Toán', '''
tập hợp|set;phần tử|element;tập con|subset;giao của hai tập hợp|intersection of two sets
hợp của hai tập hợp|union of two sets;số tự nhiên|natural number;số nguyên|integer
số hữu tỉ|rational number;số vô tỉ|irrational number;số thực|real number
giá trị tuyệt đối|absolute value;lũy thừa|power;căn bậc hai|square root
đa thức|polynomial;đơn thức|monomial;phân thức đại số|rational expression
phương trình|equation;bất phương trình|inequality;hệ phương trình|system of equations
hàm số|function;tập xác định|domain;tập giá trị|range;đồ thị hàm số|graph of a function
hàm số bậc nhất|linear function;hàm số bậc hai|quadratic function
góc lượng giác|trigonometric angle;đường tròn lượng giác|unit circle
giá trị lượng giác|trigonometric value;định lí sin|sine rule;định lí cosin|cosine rule
vectơ|vector;tích vô hướng|dot product;tọa độ|coordinates;đường thẳng|straight line
mặt phẳng|plane;đường tròn|circle;tiếp tuyến|tangent;đường kính|diameter;bán kính|radius
chu vi|perimeter;diện tích|area;thể tích|volume;độ dài cung|arc length
cấp số cộng|arithmetic sequence;cấp số nhân|geometric sequence;giới hạn|limit
đạo hàm|derivative;tích phân|integral;nguyên hàm|antiderivative
xác suất|probability;biến cố|event;không gian mẫu|sample space
trung bình cộng|arithmetic mean;trung vị|median;phương sai|variance;độ lệch chuẩn|standard deviation
'''),
    'physics': ('Vật lý', '''
độ dịch chuyển|displacement;quãng đường|distance traveled;tốc độ|speed;vận tốc|velocity
gia tốc|acceleration;chuyển động thẳng đều|uniform linear motion
chuyển động tròn đều|uniform circular motion;khối lượng|mass;trọng lượng|weight
trọng lực|gravitational force;lực ma sát|frictional force;lực đàn hồi|elastic force
động lượng|momentum;công cơ học|mechanical work;công suất|power;động năng|kinetic energy
thế năng|potential energy;cơ năng|mechanical energy;định luật bảo toàn năng lượng|law of conservation of energy
áp suất|pressure;khối lượng riêng|density;nhiệt độ|temperature;nhiệt lượng|heat
nội năng|internal energy;dao động điều hòa|simple harmonic motion;biên độ|amplitude
chu kì|period;tần số|frequency;bước sóng|wavelength;sóng cơ|mechanical wave
điện tích|electric charge;điện trường|electric field;hiệu điện thế|potential difference
cường độ dòng điện|electric current;điện trở|electrical resistance;từ trường|magnetic field
cảm ứng điện từ|electromagnetic induction;khúc xạ ánh sáng|refraction of light
phản xạ ánh sáng|reflection of light;thấu kính hội tụ|converging lens;thấu kính phân kì|diverging lens
'''),
    'chemistry': ('Hóa học', '''
nguyên tử|atom;phân tử|molecule;nguyên tố hóa học|chemical element
bảng tuần hoàn|periodic table;số hiệu nguyên tử|atomic number;đồng vị|isotope
cấu hình electron|electron configuration;liên kết ion|ionic bond;liên kết cộng hóa trị|covalent bond
phản ứng hóa học|chemical reaction;phương trình hóa học|chemical equation
chất phản ứng|reactant;sản phẩm phản ứng|reaction product;chất xúc tác|catalyst
tốc độ phản ứng|reaction rate;cân bằng hóa học|chemical equilibrium
số oxi hóa|oxidation state;chất oxi hóa|oxidizing agent;chất khử|reducing agent
dung dịch|solution;dung môi|solvent;chất tan|solute;độ tan|solubility
nồng độ phần trăm|percentage concentration;nồng độ mol|molar concentration
liên kết hydrogen|hydrogen bond;hóa học hữu cơ|organic chemistry
hợp chất hữu cơ|organic compound;công thức phân tử|molecular formula
công thức cấu tạo|structural formula;nhóm chức|functional group;đồng phân|isomer
polymer|polymer;phản ứng trùng hợp|polymerization;phản ứng thủy phân|hydrolysis
phổ hồng ngoại|infrared spectrum;khối lượng mol|molar mass
'''),
    'biology': ('Sinh học', '''
tế bào|cell;màng sinh chất|plasma membrane;tế bào chất|cytoplasm;nhân tế bào|cell nucleus
bào quan|organelle;ti thể|mitochondrion;lục lạp|chloroplast;thành tế bào|cell wall
quang hợp|photosynthesis;hô hấp tế bào|cellular respiration;trao đổi chất|metabolism
enzyme|enzyme;nguyên phân|mitosis;giảm phân|meiosis;thụ tinh|fertilization
nhiễm sắc thể|chromosome;gene|gene;kiểu gene|genotype;kiểu hình|phenotype
đột biến|mutation;di truyền|heredity;biến dị|variation;chọn lọc tự nhiên|natural selection
tiến hóa|evolution;loài|species;quần thể|population;quần xã|community
hệ sinh thái|ecosystem;chuỗi thức ăn|food chain;lưới thức ăn|food web
đa dạng sinh học|biodiversity;nhân tố sinh thái|ecological factor
cảm ứng ở sinh vật|responses to stimuli in organisms;sinh trưởng|growth;phát triển|development
hệ tuần hoàn|circulatory system;hệ hô hấp|respiratory system;hệ thần kinh|nervous system
'''),
    'computing': ('Tin học', '''
thuật toán|algorithm;dữ liệu|data;thông tin|information;biểu diễn thông tin|information representation
hệ nhị phân|binary number system;phần cứng|hardware;phần mềm|software;hệ điều hành|operating system
bộ nhớ|memory;tệp tin|file;thư mục|folder;mạng máy tính|computer network
địa chỉ IP|IP address;trình duyệt web|web browser;cơ sở dữ liệu|database
khóa chính|primary key;khóa ngoại|foreign key;truy vấn|query;bảng dữ liệu|data table
ngôn ngữ lập trình|programming language;biến|variable;hằng số|constant;kiểu dữ liệu|data type
câu lệnh điều kiện|conditional statement;vòng lặp|loop;chương trình con|subprogram
mảng|array;danh sách|list;kiểm thử|testing;gỡ lỗi|debugging
an toàn thông tin|information security;quyền riêng tư|privacy;bản quyền|copyright
trí tuệ nhân tạo|artificial intelligence;học máy|machine learning
'''),
    'technology': ('Công nghệ', '''
thiết kế kĩ thuật|engineering design;bản vẽ kĩ thuật|technical drawing
hình chiếu vuông góc|orthographic projection;hình cắt|sectional view
vật liệu cơ khí|engineering materials;gia công cơ khí|machining
truyền động|power transmission;mạch điện|electric circuit;đồ dùng điện|electrical appliance
an toàn điện|electrical safety;nguồn điện|power source;mạch điều khiển|control circuit
công nghệ trồng trọt|crop production technology;công nghệ chăn nuôi|animal husbandry technology
nông nghiệp bền vững|sustainable agriculture;thủy sản|fisheries
bảo quản thực phẩm|food preservation;chế biến thực phẩm|food processing
'''),
    'history': ('Lịch sử', '''
sử liệu|historical source;hiện vật|artifact;niên đại|chronology
thời tiền sử|prehistory;thời cổ đại|antiquity;thời trung đại|the medieval period
văn minh|civilization;nhà nước|state;đế quốc|empire;chế độ phong kiến|feudalism
cách mạng công nghiệp|Industrial Revolution;cách mạng tư sản|bourgeois revolution
chủ nghĩa thực dân|colonialism;chủ nghĩa đế quốc|imperialism;chiến tranh thế giới|World War
phong trào giải phóng dân tộc|national liberation movement;độc lập dân tộc|national independence
chủ quyền quốc gia|national sovereignty;quan hệ quốc tế|international relations
hiệp ước|treaty;di sản lịch sử|historical heritage;cải cách|reform
'''),
    'geography': ('Địa lí', '''
kinh độ|longitude;vĩ độ|latitude;đường xích đạo|equator;bản đồ|map;tỉ lệ bản đồ|map scale
địa hình|topography;khí quyển|atmosphere;thủy quyển|hydrosphere;thạch quyển|lithosphere
thời tiết|weather;khí hậu|climate;nhiệt độ không khí|air temperature;lượng mưa|precipitation
gió mùa|monsoon;dòng biển|ocean current;tài nguyên thiên nhiên|natural resources
dân số|population;mật độ dân số|population density;gia tăng dân số|population growth
đô thị hóa|urbanization;di cư|migration;cơ cấu kinh tế|economic structure
công nghiệp|industry;nông nghiệp|agriculture;dịch vụ|services
biến đổi khí hậu|climate change;phát triển bền vững|sustainable development
'''),
    'literature': ('Ngữ văn', '''
tác giả|author;tác phẩm|literary work;thể loại|genre;chủ đề|theme;đề tài|subject matter
cốt truyện|plot;nhân vật|character;người kể chuyện|narrator;ngôi kể|narrative perspective
nhân vật trữ tình|lyrical subject;hình ảnh thơ|poetic imagery;vần|rhyme;nhịp thơ|poetic rhythm
biện pháp tu từ|rhetorical device;ẩn dụ|metaphor;hoán dụ|metonymy;nhân hóa|personification
so sánh tu từ|simile;điệp ngữ|repetition;luận điểm|claim;luận cứ|supporting evidence
lập luận|argumentation;văn bản nghị luận|argumentative text;văn bản thông tin|informational text
đọc hiểu|reading comprehension;tóm tắt|summary;thông điệp|message
'''),
    'language': ('Tiếng Anh', '''
danh từ|noun;động từ|verb;tính từ|adjective;trạng từ|adverb;đại từ|pronoun;giới từ|preposition
liên từ|conjunction;mạo từ|article;chủ ngữ|subject;vị ngữ|predicate;tân ngữ|object
câu đơn|simple sentence;câu ghép|compound sentence;mệnh đề|clause
câu bị động|passive voice;câu chủ động|active voice;câu điều kiện|conditional sentence
mệnh đề quan hệ|relative clause;lời nói gián tiếp|reported speech
thì hiện tại đơn|present simple;thì quá khứ đơn|past simple;thì hiện tại hoàn thành|present perfect
âm tiết|syllable;trọng âm|word stress;ngữ điệu|intonation;phát âm|pronunciation
từ vựng|vocabulary;ngữ pháp|grammar;kĩ năng nghe|listening skill;kĩ năng nói|speaking skill
hệ thống chữ viết|writing system;tiếng mẹ đẻ|mother tongue
'''),
    'music': ('Âm nhạc', '''
cao độ|pitch;trường độ|duration;nhịp điệu|rhythm;giai điệu|melody;tiết tấu|rhythmic pattern
nhịp độ|tempo;cường độ|dynamics;âm sắc|timbre;nốt nhạc|musical note;khuông nhạc|staff
khóa Sol|treble clef;khóa Fa|bass clef;dấu lặng|rest;quãng|interval;gam|scale
hợp âm|chord;giọng trưởng|major key;giọng thứ|minor key;hòa âm|harmony
dân ca|folk song;nhạc cụ|musical instrument;hát bè|part singing
'''),
    'art': ('Mĩ thuật', '''
đường nét|line;hình khối|form;màu sắc|color;bố cục|composition;chất liệu|medium
đậm nhạt|tonal values;tương phản|contrast;phối cảnh|perspective;điểm tụ|vanishing point
tranh tĩnh vật|still life;tranh phong cảnh|landscape painting;tranh chân dung|portrait
điêu khắc|sculpture;đồ họa|graphic art;thiết kế|design;trang trí|decoration
nghệ thuật truyền thống|traditional art;di sản mĩ thuật|artistic heritage
'''),
    'citizenship': ('Giáo dục công dân', '''
tôn trọng|respect;trách nhiệm|responsibility;trung thực|honesty;nhân ái|compassion
hợp tác|cooperation;tự chủ|self-control;khoan dung|tolerance;kỉ luật|discipline
đạo đức|ethics;chuẩn mực đạo đức|moral standard;công dân|citizen;quyền con người|human rights
quyền và nghĩa vụ|rights and duties;bình đẳng|equality;công bằng|fairness
pháp luật|law;hiến pháp|constitution;nhà nước pháp quyền|the rule of law state
bảo vệ môi trường|environmental protection;kĩ năng sống|life skills
'''),
    'economics': ('Giáo dục kinh tế và pháp luật', '''
thị trường|market;cung và cầu|supply and demand;giá cả|price;cạnh tranh|competition
lạm phát|inflation;thất nghiệp|unemployment;tăng trưởng kinh tế|economic growth
phát triển kinh tế|economic development;ngân sách nhà nước|state budget
thuế|tax;tín dụng|credit;tiết kiệm|saving;đầu tư|investment;tiêu dùng|consumption
sản xuất|production;doanh nghiệp|enterprise;khởi nghiệp|entrepreneurship
quản lí tài chính cá nhân|personal financial management;hợp đồng|contract;quyền sở hữu|ownership
'''),
    'health': ('Giáo dục thể chất', '''
khởi động|warm-up;thả lỏng|cool-down;sức bền|endurance;sức mạnh|strength
tốc độ|speed;sự mềm dẻo|flexibility;khả năng phối hợp|coordination;thăng bằng|balance
thể lực|physical fitness;hoạt động thể chất|physical activity;nhịp tim|heart rate
chạy cự li ngắn|sprinting;chạy tiếp sức|relay race;nhảy xa|long jump;nhảy cao|high jump
bóng đá|football;bóng chuyền|volleyball;bóng rổ|basketball;cầu lông|badminton
chấn thương thể thao|sports injury;sơ cứu|first aid
'''),
    'heritage': ('Nội dung giáo dục của địa phương', '''
di sản văn hóa|cultural heritage;di sản văn hóa phi vật thể|intangible cultural heritage
truyền thống địa phương|local traditions;làng nghề|craft village;nghề truyền thống|traditional craft
lễ hội truyền thống|traditional festival;bản sắc văn hóa|cultural identity
cộng đồng địa phương|local community;danh lam thắng cảnh|scenic site
di tích lịch sử|historical site;bảo tồn|conservation;du lịch bền vững|sustainable tourism
văn hóa dân gian|folk culture;đa dạng văn hóa|cultural diversity
'''),
    'career': ('Hoạt động trải nghiệm, hướng nghiệp', '''
định hướng nghề nghiệp|career guidance;kĩ năng giao tiếp|communication skills
làm việc nhóm|teamwork;giải quyết vấn đề|problem solving;ra quyết định|decision making
tự nhận thức|self-awareness;quản lí thời gian|time management;mục tiêu học tập|learning goal
hoạt động cộng đồng|community activities;tình nguyện|volunteering
học tập suốt đời|lifelong learning;khám phá nghề nghiệp|career exploration
năng lực nghề nghiệp|occupational competence;kế hoạch cá nhân|personal plan
'''),
    'peace': ('Giáo dục quốc phòng và an ninh', '''
quốc phòng|national defense;an ninh quốc gia|national security;chủ quyền|sovereignty
độc lập|independence;toàn vẹn lãnh thổ|territorial integrity;biên giới quốc gia|national border
hòa bình|peace;giữ gìn hòa bình|peacekeeping;trách nhiệm công dân|civic responsibility
phòng tránh thiên tai|disaster preparedness;cứu hộ|rescue;cứu nạn|search and rescue
an toàn cộng đồng|community safety;bảo vệ Tổ quốc|national defense
'''),
    'science': ('Khoa học', '''
quan sát|observation;thí nghiệm|experiment;giả thuyết|hypothesis;đo lường|measurement
bằng chứng|evidence;kết luận khoa học|scientific conclusion;biến độc lập|independent variable
biến phụ thuộc|dependent variable;đối chứng|control;vật chất|matter;năng lượng|energy
sự biến đổi|change;môi trường sống|habitat;vòng đời|life cycle;hỗn hợp|mixture
chất tinh khiết|pure substance;sự bay hơi|evaporation;sự ngưng tụ|condensation
an toàn phòng thí nghiệm|laboratory safety
'''),
}

SUBJECT_GROUPS = {
    'Toán': ('math',), 'Vật lý': ('physics',), 'Hóa học': ('chemistry',), 'Sinh học': ('biology',),
    'Tin học': ('computing',), 'Công nghệ': ('technology',), 'Lịch sử': ('history',), 'Địa lí': ('geography',),
    'Ngữ văn': ('literature',), 'Tiếng Việt': ('literature', 'language'),
    'Tiếng dân tộc thiểu số': ('language',), 'Tiếng Anh': ('language',),
    'Ngoại ngữ 1': ('language',), 'Ngoại ngữ 2': ('language',),
    'Âm nhạc': ('music',), 'Mĩ thuật': ('art',), 'Nghệ thuật': ('music', 'art'),
    'Đạo đức': ('citizenship',), 'Giáo dục công dân': ('citizenship',),
    'Giáo dục kinh tế và pháp luật': ('citizenship', 'economics'),
    'Giáo dục thể chất': ('health',), 'Giáo dục quốc phòng và an ninh': ('peace',),
    'Hoạt động trải nghiệm': ('career',), 'Hoạt động trải nghiệm, hướng nghiệp': ('career',),
    'Nội dung giáo dục của địa phương': ('heritage',),
    'Khoa học': ('science', 'biology', 'physics', 'chemistry'),
    'Khoa học tự nhiên': ('science', 'biology', 'physics', 'chemistry'),
    'Tự nhiên và Xã hội': ('science', 'biology', 'geography', 'heritage'),
    'Lịch sử và Địa lí': ('history', 'geography'),
    'Tin học và Công nghệ': ('computing', 'technology'),
}


@lru_cache(maxsize=1)
def vocabulary():
    groups = {}
    for key, (_, text) in GROUPS.items():
        text += '\n' + EXTRA.get(key, '')
        pairs = [pair.strip() for pair in text.replace('\n', ';').split(';') if pair.strip()]
        if any(pair.count('|') != 1 or not all(part.strip() for part in pair.split('|')) for pair in pairs):
            raise ValueError('Cặp thuật ngữ nền chưa hợp lệ: ' + key)
        if len({' '.join(unicodedata.normalize('NFC', pair.split('|')[0]).casefold().split()) for pair in pairs}) != len(pairs):
            raise ValueError('Thuật ngữ nền trùng trong cùng nhóm: ' + key)
        groups[key] = [dict(vi=pair.split('|')[0], en=pair.split('|')[1], source=key) for pair in pairs]
    return groups


def terms_for(subject):
    groups = next((groups for name, groups in SUBJECT_GROUPS.items() if subject_key(name) == subject_key(subject)), ())
    rows = {}
    for group in groups:
        for row in vocabulary()[group]:
            rows.setdefault(row['vi'], {**row, 'source_url': SOURCES[row['source']][2], 'status': 'curated_reference', 'inline': False})
    return list(rows.values())


def statistics():
    return dict(version=VERSION, subjects=len(SUBJECT_GROUPS), concepts=sum(len(rows) for rows in vocabulary().values()),
                entries=sum(len(terms_for(subject)) for subject in SUBJECT_GROUPS),
                groups={key: len(rows) for key, rows in vocabulary().items()})


def seed_pack():
    from .knowledge import validate_pack

    sources = [dict(id='school-term-' + key, title=title, publisher=publisher, source_url=url,
                    official=False, source_type='editorial_reference', retrieved_at='2026-10-25',
                    notes='Nguồn tham chiếu chuyên môn; cặp Việt–Anh do BiliClass biên soạn, không phải chứng nhận của nhà xuất bản.')
               for key, (title, publisher, url) in SOURCES.items()]
    sources.append(dict(id='school-term-curriculum', title='Thông tư 17/2025/TT-BGDĐT · phạm vi chương trình',
                        publisher='Công báo Chính phủ', source_url=CURRICULUM_URL, official=True,
                        source_type='curriculum_scope', retrieved_at='2026-10-25',
                        notes='Dùng đối chiếu cơ cấu môn học; không phải nguồn từ điển song ngữ.'))
    entries = []
    for subject in SUBJECT_GROUPS:
        for row in terms_for(subject):
            digest = hashlib.sha256((subject + '|' + row['vi']).encode()).hexdigest()[:24]
            entries.append(dict(id='school-term-' + digest, subject=subject, grade='', kind='term',
                                vi=row['vi'], en=row['en'], source_ids=['school-term-' + row['source']],
                                status='reference_only', confidence='editorial_reference', updated_at='2026-10-25'))
    return validate_pack(dict(manifest=dict(format='biliknowledge', schema_version=1, pack_id=PACK_ID,
            version=VERSION, title='Thuật ngữ cơ bản theo môn · tham chiếu Việt–Anh', updated_at='2026-10-25',
            contains_full_text=False, license_note='Cặp thuật ngữ ngắn do BiliClass biên soạn. Không phải từ điển chính thức của Bộ GDĐT; không bao phủ toàn bộ chương trình.'),
            sources=sources, entries=entries))


def ensure_seed(library):
    current = library.knowledge_pack(PACK_ID)
    if current and current['version'] >= VERSION:
        return False
    library.install_knowledge_pack(seed_pack())
    return True
