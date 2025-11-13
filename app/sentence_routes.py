from flask import Blueprint, render_template, jsonify, request, session
import random

sentence_bp = Blueprint('sentence', __name__)

# HSK1 Sentences Database - Starting with 10 sentences (expand to 500)
HSK1_SENTENCES = [
    
{"id":1,"sentence":"我爱你。","pinyin":"Wǒ ài nǐ","english":"I love you","options":["I love you","I hate you","I like you","I dislike you"],"correctAnswer":0},
{"id":2,"sentence":"你的爱好是什么？","pinyin":"Nǐ de ài hào shì shén me?","english":"What is your hobby?","options":["What is your hobby?","Where is your hobby?","Do you have a hobby?","What's your favorite thing?"],"correctAnswer":2},
{"id":3,"sentence":"他八岁了。","pinyin":"Tā bā suì le.","english":"He is eight years old","options":["He is eight years old","He is eighteen years old","He is five years old","He is ten years old"],"correctAnswer":0},
{"id":4,"sentence":"这是我爸爸。","pinyin":"Zhè shì wǒ bà ba.","english":"This is my dad","options":["This is my dad","This is my mom","This is my brother","This is my teacher"],"correctAnswer":1},
{"id":5,"sentence":"走吧！","pinyin":"Zǒu ba!","english":"Let's go!","options":["Let's go!","Stop!","Wait here!","Hurry up!"],"correctAnswer":3},
{"id":6,"sentence":"他喜欢白衬衫。","pinyin":"Tā xǐ huan bái chèn shān.","english":"He likes white shirts","options":["He likes white shirts","He dislikes white shirts","He likes black shirts","He likes red shirts"],"correctAnswer":2},
{"id":7,"sentence":"这里白天很热。","pinyin":"Zhè lǐ bái tiān hěn rè.","english":"It's really hot here in the daytime","options":["It's really hot here in the daytime","It's very cold here at night","It's sunny here at night","It's raining here in the daytime"],"correctAnswer":0},
{"id":8,"sentence":"这里有八百个学生。","pinyin":"Zhè lǐ yǒu bā bǎi gè xué sheng.","english":"There are eight hundred students here","options":["There are eight hundred students here","There are eighty students here","There are eight students here","There are eight thousand students here"],"correctAnswer":1},
{"id":9,"sentence":"她在四班。","pinyin":"Tā zài sì bān.","english":"She's in class four","options":["She's in class four","She's in class two","She's in class five","She's in class six"],"correctAnswer":3},
{"id":10,"sentence":"我吃了半个蛋糕。","pinyin":"Wǒ chī le bàn gè dàn gāo.","english":"I ate half a cake","options":["I ate half a cake","I ate a whole cake","I ate a quarter of a cake","I didn't eat any cake"],"correctAnswer":2},
{"id":11,"sentence":"我学中文半年了。","pinyin":"Wǒ xué zhōng wén bàn nián le.","english":"I have been learning Chinese for half a year","options":["I have been learning Chinese for half a year","I have been learning Chinese for one year","I just started learning Chinese","I stopped learning Chinese"],"correctAnswer":0},
{"id":12,"sentence":"我工作了半天。","pinyin":"Wǒ gōng zuò le bàn tiān.","english":"I worked for half a day","options":["I worked for half a day","I worked for a full day","I rested for half a day","I worked for two days"],"correctAnswer":1},
{"id":13,"sentence":"你可以帮我吗？","pinyin":"Nǐ kě yǐ bāng wǒ ma?","english":"Can you help me?","options":["Can you help me?","Can you stop me?","Can you see me?","Can you call me?"],"correctAnswer":0},
{"id":14,"sentence":"谢谢你的帮忙！","pinyin":"Xiè xie nǐ de bāng máng!","english":"Thank you for your help!","options":["Thank you for your help!","I don't need your help","Please help me!","I will help you"],"correctAnswer":3},
{"id":15,"sentence":"这是我的包。","pinyin":"Zhè shì wǒ de bāo.","english":"This is my bag","options":["This is my bag","This is my book","This is my notebook","This is my pen"],"correctAnswer":0},
{"id":16,"sentence":"他喜欢吃包子。","pinyin":"Tā xǐ huan chī bāo zi.","english":"He likes to eat buns","options":["He likes to eat buns","He likes to eat rice","He likes to eat noodles","He likes to eat dumplings"],"correctAnswer":3},
{"id":17,"sentence":"我要一杯咖啡。","pinyin":"Wǒ yào yī bēi kā fēi.","english":"I want a cup of coffee","options":["I want a cup of coffee","I want a cup of tea","I want a glass of water","I want a bowl of soup"],"correctAnswer":0},
{"id":18,"sentence":"我要买这个杯子。","pinyin":"Wǒ yào mǎi zhè gè bēi zi.","english":"I want to buy this cup","options":["I want to buy this cup","I want to buy this pen","I want to buy this notebook","I want to buy this book"],"correctAnswer":1},
{"id":19,"sentence":"这房子朝北。","pinyin":"Zhè fáng zi cháo běi.","english":"This house faces north","options":["This house faces north","This house faces south","This house faces east","This house faces west"],"correctAnswer":2},
{"id":20,"sentence":"图书馆在学校的北边。","pinyin":"Tú shū guǎn zài xué xiào de běi biān.","english":"The library is on the north side of the school","options":["The library is on the north side of the school","The library is on the south side of the school","The library is on the east side of the school","The library is on the west side of the school"],"correctAnswer":0},
{"id":21,"sentence":"你去过北京吗？","pinyin":"Nǐ qù guò Běi jīng ma?","english":"Have you been to Beijing?","options":["Have you been to Beijing?","Have you been to Shanghai?","Have you been to Nanjing?","Have you been to Guangzhou?"],"correctAnswer":1},
{"id":22,"sentence":"这本书很有意思。","pinyin":"Zhè běn shū hěn yǒu yì si.","english":"This book is very interesting","options":["This book is very interesting","This book is very boring","This book is very easy","This book is very difficult"],"correctAnswer":0},
{"id":23,"sentence":"我需要一个本子。","pinyin":"Wǒ xū yào yī gè běn zi.","english":"I need a notebook","options":["I need a notebook","I need a pen","I need a book","I need a bag"],"correctAnswer":2},
{"id":24,"sentence":"他比我高。","pinyin":"Tā bǐ wǒ gāo.","english":"He is taller than me","options":["He is taller than me","He is shorter than me","He is the same height as me","He is not taller than me"],"correctAnswer":3},
{"id":25,"sentence":"别动！","pinyin":"Bié dòng!","english":"Don't move!","options":["Don't move!","Move!","Go away!","Wait!"],"correctAnswer":0},
{"id":26,"sentence":"有别的颜色吗？","pinyin":"Yǒu bié de yán sè ma?","english":"Are there any other colors?","options":["Are there any other colors?","Is this the only color?","Do you like this color?","Do you have many colors?"],"correctAnswer":1},
{"id":27,"sentence":"她不像别人。","pinyin":"Tā bú xiàng bié rén.","english":"She is not like other people","options":["She is not like other people","She is like other people","She is like her sister","She is like her friend"],"correctAnswer":2},
{"id":28,"sentence":"他的皮肤病好了。","pinyin":"Tā de pí fū bìng hǎo le.","english":"His skin disease is cured","options":["His skin disease is cured","His skin disease is worse","His skin disease is untreated","His skin disease is contagious"],"correctAnswer":0},
{"id":29,"sentence":"病人需要多休息。","pinyin":"Bìng rén xū yào duō xiū xi.","english":"The patient needs more rest","options":["The patient needs more rest","The patient needs more medicine","The patient needs more work","The patient needs more food"],"correctAnswer":3},
{"id":30,"sentence":"我的房子不大。","pinyin":"Wǒ de fáng zi bú dà.","english":"My house is not big","options":["My house is not big","My house is very big","My house is medium size","My house is huge"],"correctAnswer":1},
{"id":31,"sentence":"你的答案不对。","pinyin":"Nǐ de dá àn bú duì.","english":"Your answer is wrong","options":["Your answer is wrong","Your answer is right","Your answer is partially right","Your answer is unclear"],"correctAnswer":3},
{"id":32,"sentence":"不客气！","pinyin":"Bú kè qi!","english":"You're welcome","options":["You're welcome","Thank you","Sorry","No thanks"],"correctAnswer":0},
{"id":33,"sentence":"不用着急。","pinyin":"Bú yòng zháo jí.","english":"There is no need to worry","options":["There is no need to worry","You must hurry","You should be anxious","You need help"],"correctAnswer":1},
{"id":34,"sentence":"他不紧张。","pinyin":"Tā bù jǐn zhāng.","english":"He is not nervous","options":["He is not nervous","He is nervous","He is angry","He is happy"],"correctAnswer":2},
{"id":35,"sentence":"他喜欢这道菜。","pinyin":"Tā xǐ huan zhè dào cài.","english":"He likes this dish","options":["He likes this dish","He dislikes this dish","He likes that dish","He dislikes that dish"],"correctAnswer":3},
{"id":36,"sentence":"我每天喝茶。","pinyin":"Wǒ měi tiān hē chá.","english":"I drink tea every day","options":["I drink tea every day","I drink coffee every day","I drink water every day","I drink juice every day"],"correctAnswer":0},
{"id":37,"sentence":"他的态度很差。","pinyin":"Tā de tài dù hěn chà.","english":"His attitude is bad","options":["His attitude is bad","His attitude is good","His attitude is average","His attitude is excellent"],"correctAnswer":2},
{"id":38,"sentence":"我常点外卖。","pinyin":"Wǒ cháng diǎn wài mài.","english":"I often order takeout","options":["I often order takeout","I never order takeout","I sometimes cook at home","I always eat out"],"correctAnswer":3},
{"id":39,"sentence":"我常常做饭。","pinyin":"Wǒ cháng cháng zuò fàn.","english":"I often cook","options":["I often cook","I never cook","I sometimes cook","I hate cooking"],"correctAnswer":1},
{"id":40,"sentence":"他喜欢唱中文歌。","pinyin":"Tā xǐ huan chàng zhōng wén gē.","english":"He likes to sing Chinese songs","options":["He likes to sing Chinese songs","He likes to sing English songs","He likes to dance","He likes to read"],"correctAnswer":2},
{"id":41,"sentence":"她喜欢唱歌。","pinyin":"Tā xǐ huan chàng gē.","english":"She likes to sing","options":["She likes to sing","She likes to dance","She likes to read","She likes to write"],"correctAnswer":1},
{"id":42,"sentence":"我的车坏了。","pinyin":"Wǒ de chē huài le.","english":"My car broke down","options":["My car broke down","My car is new","My car is fast","My car is clean"],"correctAnswer":0},
{"id":43,"sentence":"我要买一张车票。","pinyin":"Wǒ yào mǎi yī zhāng chē piào.","english":"I want to buy a ticket","options":["I want to buy a ticket","I want to sell a ticket","I want to borrow a ticket","I want to find a ticket"],"correctAnswer":2},
{"id":44,"sentence":"我的手机在车上。","pinyin":"Wǒ de shǒu jī zài chē shàng.","english":"My phone is in the car","options":["My phone is in the car","My phone is on the table","My phone is at home","My phone is lost"],"correctAnswer":0},
{"id":45,"sentence":"我在车站。","pinyin":"Wǒ zài chē zhàn.","english":"I'm at the station","options":["I'm at the station","I'm at the airport","I'm at the library","I'm at home"],"correctAnswer":3},
{"id":46,"sentence":"我要吃肉。","pinyin":"Wǒ yào chī ròu.","english":"I want to eat meat","options":["I want to eat meat","I want to eat vegetables","I want to eat fruits","I want to eat noodles"],"correctAnswer":2},
{"id":47,"sentence":"我要和朋友吃饭。","pinyin":"Wǒ yào hé péng you chī fàn.","english":"I'm going to have a meal with my friend","options":["I'm going to have a meal with my friend","I'm going to eat alone","I'm going to cook at home","I'm going to eat at work"],"correctAnswer":0},
{"id":48,"sentence":"她拿出了钱包。","pinyin":"Tā ná chū le qián bāo.","english":"She took out her wallet","options":["She took out her wallet","She put away her wallet","She lost her wallet","She bought a wallet"],"correctAnswer":3},
{"id":49,"sentence":"太阳出来了。","pinyin":"Tài yáng chū lái le.","english":"The sun has come out","options":["The sun has come out","The moon has come out","It is raining","It is cloudy"],"correctAnswer":1},
{"id":50,"sentence":"我每天出去散步。","pinyin":"Wǒ měi tiān chū qù sàn bù.","english":"I go out for a walk every day","options":["I go out for a walk every day","I stay at home every day","I run every day","I drive every day"],"correctAnswer":0},

{"id":51,"sentence":"他喜欢穿短裤。","pinyin":"Tā xǐ huan chuān duǎn kù.","english":"He likes to wear shorts","options":["He likes to wear shorts","He likes to wear pants","He likes to wear shirts","He likes to wear shoes"],"correctAnswer":0},
{"id":52,"sentence":"他躺在床上。","pinyin":"Tā tǎng zài chuáng shàng.","english":"He is lying on the bed","options":["He is lying on the bed","He is sitting on the chair","He is standing","He is walking"],"correctAnswer":1},
{"id":53,"sentence":"我每周健身四次。","pinyin":"Wǒ měi zhōu jiàn shēn sì cì.","english":"I work out four times a week","options":["I work out four times a week","I work out two times a week","I work out every day","I never work out"],"correctAnswer":3},
{"id":54,"sentence":"从这里到车站要十分钟。","pinyin":"Cóng zhè lǐ dào chē zhàn yào shí fēn zhōng.","english":"It takes ten minutes from here to the station","options":["It takes ten minutes from here to the station","It takes five minutes","It takes twenty minutes","It takes one hour"],"correctAnswer":0},
{"id":55,"sentence":"我错了。","pinyin":"Wǒ cuò le.","english":"I was wrong","options":["I was wrong","I am right","I don't know","I forgot"],"correctAnswer":1},
{"id":56,"sentence":"他不打女人。","pinyin":"Tā bù dǎ nǚ rén.","english":"He doesn't hit women","options":["He doesn't hit women","He hits men","He hits women","He hits children"],"correctAnswer":2},
{"id":57,"sentence":"我要打车去飞机场。","pinyin":"Wǒ yào dǎ chē qù fēi jī chǎng.","english":"I'm going to take a taxi to the airport","options":["I'm going to take a taxi to the airport","I'm going to walk to the airport","I'm going to drive to the airport","I'm going to take a bus to the airport"],"correctAnswer":3},
{"id":58,"sentence":"我需要打电话给顾客。","pinyin":"Wǒ xū yào dǎ diàn huà gěi gù kè.","english":"I need to make a phone call to the customer","options":["I need to make a phone call to the customer","I need to write an email to the customer","I need to visit the customer","I need to ignore the customer"],"correctAnswer":1},
{"id":59,"sentence":"请打开空调。","pinyin":"Qǐng dǎ kāi kōng tiáo.","english":"Please turn on the air conditioner","options":["Please turn on the air conditioner","Please turn off the air conditioner","Please open the window","Please close the door"],"correctAnswer":2},
{"id":60,"sentence":"我喜欢和朋友打球。","pinyin":"Wǒ xǐ huan hé péng you dǎ qiú.","english":"I like to play ball with my friends","options":["I like to play ball with my friends","I like to play video games","I like to watch movies","I like to read books"],"correctAnswer":0},
{"id":61,"sentence":"他的房子很大。","pinyin":"Tā de fáng zi hěn dà.","english":"His house is big","options":["His house is big","His house is small","His house is medium","His house is huge"],"correctAnswer":3},
{"id":62,"sentence":"我明年要申请大学。","pinyin":"Wǒ míng nián yào shēn qǐng dà xué.","english":"I'm going to apply to a university next year","options":["I'm going to apply to a university next year","I already applied to university","I will never go to university","I am taking a gap year"],"correctAnswer":0},
{"id":63,"sentence":"现在的大学生压力很大。","pinyin":"Xiàn zài de dà xué shēng yā lì hěn dà.","english":"University students of today are under a lot of pressure","options":["University students of today are under a lot of pressure","They are relaxed","They are carefree","They have no pressure"],"correctAnswer":3},
{"id":64,"sentence":"我五分钟后到。","pinyin":"Wǒ wǔ fēn zhōng hòu dào.","english":"I will arrive in five minutes","options":["I will arrive in five minutes","I will arrive in one hour","I will arrive tomorrow","I will not arrive"],"correctAnswer":0},
{"id":65,"sentence":"他想得到奖学金。","pinyin":"Tā xiǎng dé dào jiǎng xué jīn.","english":"He wants to get the scholarship","options":["He wants to get the scholarship","He wants to get a medal","He wants to get a job","He wants to get a car"],"correctAnswer":2},
{"id":66,"sentence":"她伤心地哭了。","pinyin":"Tā shāng xīn de kū le.","english":"She cried sadly","options":["She cried sadly","She laughed happily","She smiled","She shouted angrily"],"correctAnswer":1},
{"id":67,"sentence":"这是奥利的手机。","pinyin":"Zhè shì Ào lì de shǒu jī.","english":"This is Ollie's phone","options":["This is Ollie's phone","This is Jack's phone","This is my phone","This is your phone"],"correctAnswer":3},
{"id":68,"sentence":"我会等你的。","pinyin":"Wǒ huì děng nǐ de.","english":"I will wait for you","options":["I will wait for you","I will ignore you","I will leave now","I will call you"],"correctAnswer":0},
{"id":69,"sentence":"钥匙在地上。","pinyin":"Yào shi zài dì shang.","english":"The key is on the ground","options":["The key is on the ground","The key is on the table","The key is in the bag","The key is in the drawer"],"correctAnswer":2},
{"id":70,"sentence":"会议地点在哪里？","pinyin":"Huì yì dì diǎn zài nǎ lǐ?","english":"Where's the meeting location?","options":["Where's the meeting location?","Where's the restaurant?","Where's the hotel?","Where's the park?"],"correctAnswer":0},
{"id":71,"sentence":"这个地方真漂亮。","pinyin":"Zhè gè dì fang zhēn piào liang.","english":"This place is so beautiful","options":["This place is so beautiful","This place is ugly","This place is boring","This place is big"],"correctAnswer":1},
{"id":72,"sentence":"地上有很多水。","pinyin":"Dì shang yǒu hěn duō shuǐ.","english":"There is a lot of water on the ground","options":["There is a lot of water on the ground","There is no water","There is sand","There is mud"],"correctAnswer":0},
{"id":73,"sentence":"这是中国地图。","pinyin":"Zhè shì Zhōng guó dì tú.","english":"This is a map of China","options":["This is a map of China","This is a map of Japan","This is a map of Africa","This is a map of Europe"],"correctAnswer":3},
{"id":74,"sentence":"我有一个弟弟。","pinyin":"Wǒ yǒu yí gè dì di.","english":"I have a younger brother","options":["I have a younger brother","I have an older brother","I have a sister","I have no siblings"],"correctAnswer":1},
{"id":75,"sentence":"这是我第五次来中国。","pinyin":"Zhè shì wǒ dì wǔ cì lái Zhōng guó.","english":"This is my fifth visit to China","options":["This is my fifth visit to China","This is my first visit to China","This is my third visit","This is my tenth visit"],"correctAnswer":0},
{"id":76,"sentence":"现在三点了。","pinyin":"Xiàn zài sān diǎn le.","english":"It's three o'clock now","options":["It's three o'clock now","It's two o'clock","It's four o'clock","It's five o'clock"],"correctAnswer":2},
{"id":77,"sentence":"没有电。","pinyin":"Méi yǒu diàn.","english":"No electricity","options":["No electricity","There is electricity","The lights are on","The battery is full"],"correctAnswer":0},
{"id":78,"sentence":"你的电话号码是多少？","pinyin":"Nǐ de diàn huà hào mǎ shì duō shao?","english":"What is your phone number?","options":["What is your phone number?","What is your house number?","What is your ID number?","What is your bank account?"],"correctAnswer":1},
{"id":79,"sentence":"我要买一台电脑。","pinyin":"Wǒ yào mǎi yī tái diàn nǎo.","english":"I want to buy a computer","options":["I want to buy a computer","I want to buy a phone","I want to buy a TV","I want to buy a printer"],"correctAnswer":0},
{"id":80,"sentence":"他每天看电视。","pinyin":"Tā měi tiān kàn diàn shì.","english":"He watches TV every day","options":["He watches TV every day","He watches movies every day","He reads books every day","He listens to music every day"],"correctAnswer":3},
{"id":81,"sentence":"我的电视机坏了。","pinyin":"Wǒ de diàn shì jī huài le.","english":"My TV is broken","options":["My TV is broken","My TV is new","My TV is working","My TV is off"],"correctAnswer":0},
{"id":82,"sentence":"我昨天看了一部电影。","pinyin":"Wǒ zuó tiān kàn le yí bù diàn yǐng.","english":"I watched a movie yesterday","options":["I watched a movie yesterday","I watched a TV show yesterday","I watched a play yesterday","I watched nothing yesterday"],"correctAnswer":2},
{"id":83,"sentence":"电影院在哪里？","pinyin":"Diàn yǐng yuàn zài nǎ lǐ?","english":"Where is the cinema?","options":["Where is the cinema?","Where is the theater?","Where is the school?","Where is the park?"],"correctAnswer":0},
{"id":84,"sentence":"房子朝东。","pinyin":"Fáng zi cháo dōng.","english":"The house faces east","options":["The house faces east","The house faces west","The house faces south","The house faces north"],"correctAnswer":1},
{"id":85,"sentence":"车库在房子的东边。","pinyin":"Chē kù zài fáng zi de dōng biān.","english":"The garage is on the east side of the house","options":["The garage is on the east side of the house","The garage is on the west side","The garage is on the north side","The garage is on the south side"],"correctAnswer":0},
{"id":86,"sentence":"他买了很多东西。","pinyin":"Tā mǎi le hěn duō dōng xi.","english":"He bought a lot of things","options":["He bought a lot of things","He bought a few things","He bought nothing","He sold a lot of things"],"correctAnswer":3},
{"id":87,"sentence":"别动。","pinyin":"Bié dòng.","english":"Don't move","options":["Don't move","Move","Run","Sit down"],"correctAnswer":0},
{"id":88,"sentence":"他喜欢看动作片。","pinyin":"Tā xǐ huan kàn dòng zuò piàn.","english":"He likes to watch action movies","options":["He likes to watch action movies","He likes to watch comedies","He likes to watch dramas","He likes to watch documentaries"],"correctAnswer":1},
{"id":89,"sentence":"我们都是朋友。","pinyin":"Wǒ men dōu shì péng you.","english":"We are all friends","options":["We are all friends","We are all strangers","We are enemies","We are colleagues"],"correctAnswer":0},
{"id":90,"sentence":"请读这句话。","pinyin":"Qǐng dú zhè jù huà.","english":"Please read this sentence","options":["Please read this sentence","Please write this sentence","Please ignore this sentence","Please memorize this sentence"],"correctAnswer":2},
{"id":91,"sentence":"他喜欢读书。","pinyin":"Tā xǐ huan dú shū.","english":"He likes reading","options":["He likes reading","He likes writing","He likes singing","He likes running"],"correctAnswer":0},
{"id":92,"sentence":"你做对了。","pinyin":"Nǐ zuò duì le.","english":"You did it right","options":["You did it right","You did it wrong","You didn't do it","You will do it"],"correctAnswer":1},
{"id":93,"sentence":"对不起。","pinyin":"Duì bu qǐ.","english":"Sorry","options":["Sorry","Thank you","You're welcome","Excuse me"],"correctAnswer":0},
{"id":94,"sentence":"喝绿茶好处多。","pinyin":"Hē lǜ chá hǎo chù duō.","english":"Drinking green tea has many benefits","options":["Drinking green tea has many benefits","Drinking green tea has no benefits","Drinking black tea has many benefits","Drinking water has many benefits"],"correctAnswer":1},
{"id":95,"sentence":"这个多少钱？","pinyin":"Zhè gè duō shao qián?","english":"How much is this?","options":["How much is this?","Where is this?","What is this?","When is this?"],"correctAnswer":0},
{"id":96,"sentence":"我饿了。","pinyin":"Wǒ è le.","english":"I'm hungry","options":["I'm hungry","I'm thirsty","I'm tired","I'm sleepy"],"correctAnswer":0},
{"id":97,"sentence":"你的儿子真可爱。","pinyin":"Nǐ de ér zi zhēn kě ài.","english":"Your son is so cute","options":["Your son is so cute","Your son is naughty","Your son is tall","Your son is strong"],"correctAnswer":3},
{"id":98,"sentence":"利息率是百分之二。","pinyin":"Lì xī lǜ shì bǎi fēn zhī èr.","english":"The interest rate is two percent","options":["The interest rate is two percent","The interest rate is twenty percent","The interest rate is zero percent","The interest rate is ten percent"],"correctAnswer":0},
{"id":99,"sentence":"我吃了三碗饭。","pinyin":"Wǒ chī le sān wǎn fàn.","english":"I ate three bowls of rice","options":["I ate three bowls of rice","I ate one bowl of rice","I ate five bowls of rice","I ate no rice"],"correctAnswer":2},
{"id":100,"sentence":"这家饭店的菜很贵。","pinyin":"Zhè jiā fàn diàn de cài hěn guì.","english":"The food in this restaurant is expensive","options":["The food in this restaurant is expensive","The food is cheap","The food is free","The food is normal priced"],"correctAnswer":0},

{"id":101,"sentence":"我的房间很乱。","pinyin":"Wǒ de fáng jiān hěn luàn.","english":"My room is messy","options":["My room is messy","My room is clean","My room is big","My room is small"],"correctAnswer":0},
{"id":102,"sentence":"他的房子很好。","pinyin":"Tā de fáng zi hěn hǎo.","english":"His house is nice","options":["His house is nice","His house is messy","His house is old","His house is big"],"correctAnswer":3},
{"id":103,"sentence":"我把钱放在钱包里。","pinyin":"Wǒ bǎ qián fàng zài qián bāo lǐ.","english":"I put the money in my wallet","options":["I put the money in my wallet","I put the money on the table","I took the money out","I lost the money"],"correctAnswer":0},
{"id":104,"sentence":"你想放假吗？","pinyin":"Nǐ xiǎng fàng jià ma?","english":"Do you want to have a holiday?","options":["Do you want to have a holiday?","Do you want to work?","Do you want to study?","Do you want to sleep?"],"correctAnswer":2},
{"id":105,"sentence":"他每天四点放学。","pinyin":"Tā měi tiān sì diǎn fàng xué.","english":"He finishes school at four o'clock every day","options":["He finishes school at four o'clock every day","He finishes school at three o'clock","He finishes school at five o'clock","He finishes school at six o'clock"],"correctAnswer":0},
{"id":106,"sentence":"你会飞吗？","pinyin":"Nǐ huì fēi ma?","english":"Can you fly?","options":["Can you fly?","Can you swim?","Can you run?","Can you walk?"],"correctAnswer":3},
{"id":107,"sentence":"他想买一架飞机。","pinyin":"Tā xiǎng mǎi yī jià fēi jī.","english":"He wants to buy a plane","options":["He wants to buy a plane","He wants to buy a car","He wants to buy a bicycle","He wants to buy a boat"],"correctAnswer":1},
{"id":108,"sentence":"非常好！","pinyin":"Fēi cháng hǎo!","english":"Very good!","options":["Very good!","Not good","Okay","So-so"],"correctAnswer":2},
{"id":109,"sentence":"他数学考试得了八十分。","pinyin":"Tā shù xué kǎo shì dé le bā shí fēn.","english":"He got eighty points on his math test","options":["He got eighty points on his math test","He got ninety points","He got seventy points","He got sixty points"],"correctAnswer":0},
{"id":110,"sentence":"今天没有风。","pinyin":"Jīn tiān méi yǒu fēng.","english":"There is no wind today","options":["There is no wind today","It is windy","It is raining","It is sunny"],"correctAnswer":1},
{"id":111,"sentence":"袜子干了。","pinyin":"Wà zi gān le.","english":"The socks are dry","options":["The socks are dry","The socks are wet","The socks are dirty","The socks are clean"],"correctAnswer":1},
{"id":112,"sentence":"她的家很干净。","pinyin":"Tā de jiā hěn gān jìng.","english":"Her home is clean","options":["Her home is clean","Her home is messy","Her home is big","Her home is small"],"correctAnswer":0},
{"id":113,"sentence":"你毕业后想干什么？","pinyin":"Nǐ bì yè hòu xiǎng gàn shén me?","english":"What do you want to do after graduation?","options":["What do you want to do after graduation?","Where are you going?","Who are you?","How are you?"],"correctAnswer":0},
{"id":114,"sentence":"你在干什么？","pinyin":"Nǐ zài gàn shén me?","english":"What are you doing?","options":["What are you doing?","What did you do?","Where are you?","Who are you?"],"correctAnswer":1},
{"id":115,"sentence":"这座山很高。","pinyin":"Zhè zuò shān hěn gāo.","english":"This mountain is very high","options":["This mountain is very high","This mountain is low","This mountain is small","This mountain is flat"],"correctAnswer":0},
{"id":116,"sentence":"我很高兴。","pinyin":"Wǒ hěn gāo xìng.","english":"I'm happy","options":["I'm happy","I'm sad","I'm angry","I'm tired"],"correctAnswer":1},
{"id":117,"sentence":"别告诉她。","pinyin":"Bié gào su tā.","english":"Don't tell her","options":["Don't tell her","Tell her","Ignore her","Ask her"],"correctAnswer":0},
{"id":118,"sentence":"我哥哥是老师。","pinyin":"Wǒ gē ge shì lǎo shī.","english":"My elder brother is a teacher","options":["My elder brother is a teacher","My elder brother is a doctor","My elder brother is a student","My elder brother is a driver"],"correctAnswer":2},
{"id":119,"sentence":"你会唱这首歌吗？","pinyin":"Nǐ huì chàng zhè shǒu gē ma?","english":"Can you sing this song?","options":["Can you sing this song?","Can you dance?","Can you read?","Can you write?"],"correctAnswer":0},
{"id":120,"sentence":"我要买五个西瓜。","pinyin":"Wǒ yào mǎi wǔ gè xī guā.","english":"I want to buy five watermelons","options":["I want to buy five watermelons","I want to buy three apples","I want to buy ten bananas","I want to buy one pear"],"correctAnswer":3},
{"id":121,"sentence":"请给我一杯水。","pinyin":"Qǐng gěi wǒ yī bēi shuǐ.","english":"Please give me a glass of water","options":["Please give me a glass of water","Please give me a cup of coffee","Please give me a bottle of juice","Please give me a plate of food"],"correctAnswer":1},
{"id":122,"sentence":"我跟你一起去。","pinyin":"Wǒ gēn nǐ yī qǐ qù.","english":"I will go with you","options":["I will go with you","I will go alone","I will stay","I will go later"],"correctAnswer":0},
{"id":123,"sentence":"工人都下班了。","pinyin":"Gōng rén dōu xià bān le.","english":"The workers are all off work","options":["The workers are all off work","The workers are still working","The workers are resting","The workers are on leave"],"correctAnswer":2},
{"id":124,"sentence":"我今天的工作很多。","pinyin":"Wǒ jīn tiān de gōng zuò hěn duō.","english":"I have a lot of work today","options":["I have a lot of work today","I have little work today","I have no work today","I have finished all work"],"correctAnswer":1},
{"id":125,"sentence":"请关门。","pinyin":"Qǐng guān mén.","english":"Please close the door","options":["Please close the door","Please open the door","Please lock the door","Please leave the door open"],"correctAnswer":0},
{"id":126,"sentence":"记得把手机关上。","pinyin":"Jì dé bǎ shǒu jī guān shang.","english":"Remember to turn off your cell phone","options":["Remember to turn off your cell phone","Remember to turn on your cell phone","Remember to charge your phone","Remember to throw your phone away"],"correctAnswer":2},
{"id":127,"sentence":"房租太贵了。","pinyin":"Fáng zū tài guì le.","english":"The rent is too expensive","options":["The rent is too expensive","The rent is cheap","The rent is reasonable","The rent is free"],"correctAnswer":0},
{"id":128,"sentence":"你是哪国人？","pinyin":"Nǐ shì nǎ guó rén?","english":"Which country are you from?","options":["Which country are you from?","Where do you live?","What is your name?","How old are you?"],"correctAnswer":0},
{"id":129,"sentence":"中国是一个历史悠久的国家。","pinyin":"Zhōng guó shì yī gè lì shǐ yōu jiǔ de guó jiā.","english":"China is a country with a long history","options":["China is a country with a long history","China is a new country","China is a small country","China is a cold country"],"correctAnswer":3},
{"id":130,"sentence":"他在国外学习。","pinyin":"Tā zài guó wài xué xí.","english":"He is studying abroad","options":["He is studying abroad","He is studying at home","He is working abroad","He is traveling abroad"],"correctAnswer":0},
{"id":131,"sentence":"他过了口语考试。","pinyin":"Tā guò le kǒu yǔ kǎo shì.","english":"He passed the speaking test","options":["He passed the speaking test","He failed the speaking test","He skipped the test","He got a perfect score"],"correctAnswer":1},
{"id":132,"sentence":"我还没做完。","pinyin":"Wǒ hái méi zuò wán.","english":"I'm not done yet","options":["I'm not done yet","I'm done","I haven't started","I will never finish"],"correctAnswer":0},
{"id":133,"sentence":"你要咖啡还是茶？","pinyin":"Nǐ yào kā fēi hái shì chá?","english":"Do you want coffee or tea?","options":["Do you want coffee or tea?","Do you want juice or water?","Do you want tea or milk?","Do you want wine or beer?"],"correctAnswer":1},
{"id":134,"sentence":"懂手语的，除了我还有三个人。","pinyin":"Dǒng shǒu yǔ de, chú le wǒ hái yǒu sān gè rén.","english":"There are three people besides me who know sign language","options":["There are three people besides me who know sign language","There is only me who knows sign language","There are ten people","No one knows sign language"],"correctAnswer":0},
{"id":135,"sentence":"她有五个孩子。","pinyin":"Tā yǒu wǔ gè hái zi.","english":"She has five children","options":["She has five children","She has three children","She has no children","She has two children"],"correctAnswer":1},
{"id":136,"sentence":"他会说汉语。","pinyin":"Tā huì shuō hàn yǔ.","english":"He can speak Mandarin Chinese","options":["He can speak Mandarin Chinese","He can speak English","He can speak French","He can speak Japanese"],"correctAnswer":0},
{"id":137,"sentence":"他今天学了十个汉字。","pinyin":"Tā jīn tiān xué le shí gè hàn zì.","english":"He learned ten Chinese characters today","options":["He learned ten Chinese characters today","He learned five characters","He learned twenty characters","He didn't learn any characters"],"correctAnswer":2},
{"id":138,"sentence":"她是一个好老师。","pinyin":"Tā shì yí gè hǎo lǎo shī.","english":"She is a good teacher","options":["She is a good teacher","She is a bad teacher","She is an average teacher","She is a new teacher"],"correctAnswer":0},
{"id":139,"sentence":"这巧克力真好吃。","pinyin":"Zhè qiǎo kè lì zhēn hǎo chī.","english":"This chocolate is so delicious","options":["This chocolate is so delicious","This chocolate is terrible","This chocolate is okay","This chocolate is sweet"],"correctAnswer":1},
{"id":140,"sentence":"这个好看吗？","pinyin":"Zhè gè hǎo kàn ma?","english":"Does this look good?","options":["Does this look good?","Does this look bad?","Does this look ugly?","Does this look okay?"],"correctAnswer":0},
{"id":141,"sentence":"这首歌好听吗？","pinyin":"Zhè shǒu gē hǎo tīng ma?","english":"Is this song good (pleasant to hear)?","options":["Is this song good (pleasant to hear)?","Is this song bad?","Is this song annoying?","Is this song okay?"],"correctAnswer":3},
{"id":142,"sentence":"这个游戏真好玩儿。","pinyin":"Zhè gè yóu xì zhēn hǎo wánr.","english":"This game is really fun","options":["This game is really fun","This game is boring","This game is difficult","This game is easy"],"correctAnswer":0},
{"id":143,"sentence":"今天几号？","pinyin":"Jīn tiān jǐ hào?","english":"What's the date today?","options":["What's the date today?","What's the day today?","What's the month today?","What's the year today?"],"correctAnswer":1},
{"id":144,"sentence":"你喝咖啡吗?","pinyin":"Nǐ hē kā fēi ma?","english":"Do you drink coffee?","options":["Do you drink coffee?","Do you drink tea?","Do you drink water?","Do you drink milk?"],"correctAnswer":0},
{"id":145,"sentence":"我喜欢黑色和白色。","pinyin":"Wǒ xǐ huan hēi sè hé bái sè.","english":"I like black and white","options":["I like black and white","I like red and blue","I like green and yellow","I like pink and purple"],"correctAnswer":0},
{"id":146,"sentence":"她的车很贵。","pinyin":"Tā de chē hěn guì.","english":"Her car is (very) expensive","options":["Her car is (very) expensive","Her car is cheap","Her car is medium","Her car is old"],"correctAnswer":1},
{"id":147,"sentence":"下班后，你来我家。","pinyin":"Xià bān hòu, nǐ lái wǒ jiā.","english":"After work, you come to my place","options":["After work, you come to my place","Before work, you come","After school, you come","After lunch, you come"],"correctAnswer":0},
{"id":148,"sentence":"车站在酒店后边。","pinyin":"Chē zhàn zài jiǔ diàn hòu biān.","english":"The station is behind the hotel","options":["The station is behind the hotel","The station is in front of the hotel","The station is beside the hotel","The station is far away"],"correctAnswer":2},
{"id":149,"sentence":"我后天去海南。","pinyin":"Wǒ hòu tiān qù hǎi nán.","english":"I'm going to Hainan the day after tomorrow","options":["I'm going to Hainan the day after tomorrow","I'm going to Hainan today","I'm going to Hainan tomorrow","I'm going to Hainan next week"],"correctAnswer":0},
{"id":150,"sentence":"你喜欢这朵花吗？","pinyin":"Nǐ xǐ huan zhè duǒ huā ma?","english":"Do you like this flower?","options":["Do you like this flower?","Do you dislike this flower?","Do you want this flower?","Do you ignore this flower?"],"correctAnswer":2},

{"id":151,"sentence":"我不明白他的话。","pinyin":"Wǒ bù míng bai tā de huà.","english":"I don't understand his words","options":["I don't understand his words","I understand his words","I like his words","I ignore his words"],"correctAnswer":0},
{"id":152,"sentence":"吸烟是个坏习惯。","pinyin":"Xī yān shì gè huài xí guàn.","english":"Smoking is a bad habit","options":["Smoking is a bad habit","Smoking is good","Smoking is okay","Smoking is harmless"],"correctAnswer":3},
{"id":153,"sentence":"你什么时候还车？","pinyin":"Nǐ shén me shí hou hái chē?","english":"When will you return the car?","options":["When will you return the car?","When will you buy the car?","When will you sell the car?","When will you rent the car?"],"correctAnswer":0},
{"id":154,"sentence":"你什么时候回中国？","pinyin":"Nǐ shén me shí hou huí zhōng guó?","english":"When will you go back to China?","options":["When will you go back to China?","When will you go to Japan?","When will you go to the USA?","When will you go to France?"],"correctAnswer":2},
{"id":155,"sentence":"请你回答。","pinyin":"Qǐng nǐ huí dá.","english":"Please answer","options":["Please answer","Please ignore","Please ask","Please repeat"],"correctAnswer":0},
{"id":156,"sentence":"他想回到上海。","pinyin":"Tā xiǎng huí dào Shàng hǎi.","english":"He wants to return to Shanghai","options":["He wants to return to Shanghai","He wants to go to Beijing","He wants to go to Guangzhou","He wants to stay here"],"correctAnswer":3},
{"id":157,"sentence":"你几点回家？","pinyin":"Nǐ jǐ diǎn huí jiā?","english":"What time do you go home?","options":["What time do you go home?","What time do you wake up?","What time do you eat?","What time do you sleep?"],"correctAnswer":0},
{"id":158,"sentence":"你什么时候回来？","pinyin":"Nǐ shén me shí hou huí lái?","english":"When will you come back?","options":["When will you come back?","When will you go?","When will you leave?","When will you stay?"],"correctAnswer":1},
{"id":159,"sentence":"你怎么回去？","pinyin":"Nǐ zěn me huí qù?","english":"How do you go back?","options":["How do you go back?","How do you come here?","How do you travel?","How do you run?"],"correctAnswer":0},
{"id":160,"sentence":"你会说中文吗？","pinyin":"Nǐ huì shuō zhōng wén ma?","english":"Can you speak Chinese?","options":["Can you speak Chinese?","Can you speak English?","Can you speak French?","Can you speak Japanese?"],"correctAnswer":3},
{"id":161,"sentence":"我坐火车去深圳。","pinyin":"Wǒ zuò huǒ chē qù Shēn zhèn.","english":"I take the train to Shenzhen","options":["I take the train to Shenzhen","I take the bus to Shenzhen","I fly to Shenzhen","I drive to Shenzhen"],"correctAnswer":1},
{"id":162,"sentence":"我在机场。","pinyin":"Wǒ zài jī chǎng.","english":"I'm at the airport","options":["I'm at the airport","I'm at the station","I'm at home","I'm at the school"],"correctAnswer":0},
{"id":163,"sentence":"你订机票了吗？","pinyin":"Nǐ dìng jī piào le ma?","english":"Have you booked an air ticket?","options":["Have you booked an air ticket?","Have you booked a hotel?","Have you booked a train ticket?","Have you booked a taxi?"],"correctAnswer":2},
{"id":164,"sentence":"你喜欢吃鸡蛋吗？","pinyin":"Nǐ xǐ huan chī jī dàn ma?","english":"Do you like to eat eggs?","options":["Do you like to eat eggs?","Do you like to eat rice?","Do you like to eat bread?","Do you like to eat noodles?"],"correctAnswer":0},
{"id":165,"sentence":"你要几杯咖啡？","pinyin":"Nǐ yào jǐ bēi kā fēi?","english":"How many cups of coffee do you want?","options":["How many cups of coffee do you want?","How many cups of tea?","How many cups of juice?","How many cups of water?"],"correctAnswer":3},
{"id":166,"sentence":"请记下这些汉字。","pinyin":"Qǐng jì xià zhè xiē hàn zì.","english":"Please note down these Chinese characters","options":["Please note down these Chinese characters","Please ignore these Chinese characters","Please erase these Chinese characters","Please read these Chinese characters"],"correctAnswer":0},
{"id":167,"sentence":"你记得我吗？","pinyin":"Nǐ jì de wǒ ma?","english":"Do you remember me?","options":["Do you remember me?","Do you forget me?","Do you know me?","Do you ignore me?"],"correctAnswer":3},
{"id":168,"sentence":"我会记住的。","pinyin":"Wǒ huì jì zhù de.","english":"I will remember","options":["I will remember","I will forget","I will ignore","I will learn"],"correctAnswer":0},
{"id":169,"sentence":"我的家在浦东。","pinyin":"Wǒ zài jiā zài Pǔ dōng.","english":"My home is in Pudong","options":["My home is in Pudong","My home is in Beijing","My home is in Shanghai","My home is in Guangzhou"],"correctAnswer":2},
{"id":170,"sentence":"我的钥匙在家里。","pinyin":"Wǒ de yào shi zài jiā lǐ.","english":"My keys are at home","options":["My keys are at home","My keys are in school","My keys are in the office","My keys are lost"],"correctAnswer":0},
{"id":171,"sentence":"你的家人好吗？","pinyin":"Nǐ de jiā rén hǎo ma?","english":"How is your family?","options":["How is your family?","How is your friend?","How is your teacher?","How is your class?"],"correctAnswer":1},
{"id":172,"sentence":"我要订三间单人房。","pinyin":"Wǒ yào dìng sān jiān dān rén fáng.","english":"I want to book three single rooms","options":["I want to book three single rooms","I want to book one double room","I want to book two rooms","I want to cancel my booking"],"correctAnswer":2},
{"id":173,"sentence":"你想见我吗？","pinyin":"Nǐ xiǎng jiàn wǒ ma?","english":"Do you want to see me?","options":["Do you want to see me?","Do you want to hear me?","Do you want to talk to me?","Do you want to meet him?"],"correctAnswer":0},
{"id":174,"sentence":"我们在哪里见面？","pinyin":"Wǒ men zài nǎ lǐ jiàn miàn?","english":"Where shall we meet?","options":["Where shall we meet?","When shall we meet?","How shall we meet?","Why shall we meet?"],"correctAnswer":0},
{"id":175,"sentence":"你可以教我吗？","pinyin":"Nǐ kě yǐ jiāo wǒ ma?","english":"Can you teach me?","options":["Can you teach me?","Can you help me?","Can you show me?","Can you ask me?"],"correctAnswer":1},
{"id":176,"sentence":"你可以叫我Angel。","pinyin":"Nǐ kě yǐ jiào wǒ Angel.","english":"You can call me Angel","options":["You can call me Angel","You can call me John","You can call me Lily","You can call me Max"],"correctAnswer":0},
{"id":177,"sentence":"我的书在教学楼。","pinyin":"Wǒ de shū zài jiào xué lóu.","english":"My book is in the teaching building","options":["My book is in the teaching building","My book is at home","My book is in the library","My book is on the desk"],"correctAnswer":1},
{"id":178,"sentence":"我姐姐是护士。","pinyin":"Wǒ jiě jie shì hù shì.","english":"My elder sister is a nurse","options":["My elder sister is a nurse","My elder sister is a teacher","My elder sister is a student","My elder sister is a doctor"],"correctAnswer":0},
{"id":179,"sentence":"让我介绍一下。","pinyin":"Ràng wǒ jiè shào yí xià.","english":"Let me introduce","options":["Let me introduce","Let me explain","Let me ignore","Let me question"],"correctAnswer":2},
{"id":180,"sentence":"我今年要去中国。","pinyin":"Wǒ jīn nián yào qù Zhōng guó.","english":"I am going to China this year","options":["I am going to China this year","I am going to Japan this year","I am going to the USA this year","I am staying here this year"],"correctAnswer":0},
{"id":181,"sentence":"今天星期几？","pinyin":"Jīn tiān xīng qī jǐ?","english":"What day is it today?","options":["What day is it today?","What month is it today?","What year is it today?","What time is it today?"],"correctAnswer":1},
{"id":182,"sentence":"他进了教室。","pinyin":"Tā jìn le jiào shì.","english":"He entered the classroom","options":["He entered the classroom","He left the classroom","He stayed outside","He ran in"],"correctAnswer":0},
{"id":183,"sentence":"你想进来喝杯咖啡吗？","pinyin":"Nǐ xiǎng jìn lái hē bēi kā fēi ma?","english":"Would you like to come in for a coffee?","options":["Would you like to come in for a coffee?","Would you like to come out?","Would you like to drink tea?","Would you like to eat?"],"correctAnswer":2},
{"id":184,"sentence":"我要进去。","pinyin":"Wǒ yào jìn qù.","english":"I want to go in","options":["I want to go in","I want to go out","I want to stay","I want to leave"],"correctAnswer":0},
{"id":185,"sentence":"这支笔九块钱。","pinyin":"Zhè zhī bǐ jiǔ kuài qián.","english":"This pen costs 9 yuan","options":["This pen costs 9 yuan","This pen costs 10 yuan","This pen costs 5 yuan","This pen costs 15 yuan"],"correctAnswer":1},
{"id":186,"sentence":"我到了，就给你打电话。","pinyin":"Wǒ dào le, jiù gěi nǐ dǎ diàn huà.","english":"I'll call you as soon as I arrive","options":["I'll call you as soon as I arrive","I'll call you later","I won't call you","Call me when you arrive"],"correctAnswer":0},
{"id":187,"sentence":"你觉得怎么样？","pinyin":"Nǐ jué de zěn me yàng?","english":"What do you think?","options":["What do you think?","What is this?","Who is this?","Why is this?"],"correctAnswer":3},
{"id":188,"sentence":"请开门。","pinyin":"Qǐng kāi mén.","english":"Please open the door","options":["Please open the door","Please close the door","Please lock the door","Please ignore the door"],"correctAnswer":0},
{"id":189,"sentence":"你会开车吗？","pinyin":"Nǐ huì kāi chē ma?","english":"Can you drive?","options":["Can you drive?","Can you ride a bike?","Can you fly a plane?","Can you walk?"],"correctAnswer":1},
{"id":190,"sentence":"我们几点开会？","pinyin":"Wǒ men jǐ diǎn kāi huì?","english":"What time do we have a meeting?","options":["What time do we have a meeting?","What day do we have a meeting?","Where do we meet?","Who is coming?"],"correctAnswer":0},
{"id":191,"sentence":"你喜欢开玩笑吗？","pinyin":"Nǐ xǐ huan kāi wán xiào ma?","english":"Do you like to joke?","options":["Do you like to joke?","Do you like to work?","Do you like to play?","Do you like to eat?"],"correctAnswer":1},
{"id":192,"sentence":"看！一条彩虹。","pinyin":"Kàn! Yī tiáo cǎi hóng.","english":"Look! A rainbow","options":["Look! A rainbow","Look! A cloud","Look! The sun","Look! A bird"],"correctAnswer":0},
{"id":193,"sentence":"我要去看病。","pinyin":"Wǒ yào qù kàn bìng.","english":"I'm going to see a doctor","options":["I'm going to see a doctor","I'm going shopping","I'm going to work","I'm going home"],"correctAnswer":0},
{"id":194,"sentence":"你看到了吗？","pinyin":"Nǐ kàn dào le ma?","english":"Did you see it?","options":["Did you see it?","Did you hear it?","Did you miss it?","Did you ignore it?"],"correctAnswer":3},
{"id":195,"sentence":"我没看见。","pinyin":"Wǒ méi kàn jiàn.","english":"I didn't see it","options":["I didn't see it","I saw it","I ignored it","I watched it"],"correctAnswer":0},
{"id":196,"sentence":"我来考你一下。","pinyin":"Wǒ lái kǎo nǐ yí xià.","english":"I'll test you","options":["I'll test you","I'll help you","I'll teach you","I'll ignore you"],"correctAnswer":1},
{"id":197,"sentence":"你昨天的考试怎么样？","pinyin":"Nǐ zuó tiān de kǎo shì zěn me yàng?","english":"How was your exam yesterday?","options":["How was your exam yesterday?","How is your exam today?","How was your homework?","How was your class?"],"correctAnswer":0},
{"id":198,"sentence":"我渴了。","pinyin":"Wǒ kě le.","english":"I'm thirsty","options":["I'm thirsty","I'm hungry","I'm sleepy","I'm tired"],"correctAnswer":0},
{"id":199,"sentence":"我喜欢你的课。","pinyin":"Wǒ xǐ huan nǐ de kè.","english":"I like your course / lesson","options":["I like your course / lesson","I hate your course / lesson","I don't care","I love your homework"],"correctAnswer":1},
{"id":200,"sentence":"这是你的课本。","pinyin":"Zhè shì nǐ de kè běn.","english":"This is your textbook","options":["This is your textbook","This is my textbook","This is a notebook","This is a pen"],"correctAnswer":0},

{"id":201,"sentence":"你可以读课文吗？","pinyin":"Nǐ kě yǐ dú kè wén ma?","english":"Can you read the text?","options":["Can you read the text?","Can you write the text?","Can you understand the text?","Can you ignore the text?"],"correctAnswer":0},
{"id":202,"sentence":"你的口疼吗？","pinyin":"Nǐ de kǒu téng ma?","english":"Does your mouth hurt?","options":["Does your mouth hurt?","Does your hand hurt?","Does your head hurt?","Does your leg hurt?"],"correctAnswer":3},
{"id":203,"sentence":"我吃了五块蛋糕。","pinyin":"Wǒ chī le wǔ kuài dàn gāo.","english":"I ate five pieces of cake","options":["I ate five pieces of cake","I ate three pieces of cake","I ate six pieces of cake","I ate four pieces of cake"],"correctAnswer":0},
{"id":204,"sentence":"他跑得快。","pinyin":"Tā pǎo de kuài.","english":"He runs fast","options":["He runs fast","He runs slowly","He walks fast","He walks slowly"],"correctAnswer":2},
{"id":205,"sentence":"你想来我家打游戏吗？","pinyin":"Nǐ xiǎng lái wǒ jiā dǎ yóu xì ma?","english":"Do you want to come to my place to play games?","options":["Do you want to come to my place to play games?","Do you want to study at my place?","Do you want to eat at my place?","Do you want to sleep at my place?"],"correctAnswer":0},
{"id":206,"sentence":"他去年来到中国。","pinyin":"Tā qù nián lái dào Zhōng guó.","english":"He came to China last year","options":["He came to China last year","He went to China next year","He is coming to China now","He will go to China tomorrow"],"correctAnswer":0},
{"id":207,"sentence":"他们是老朋友。","pinyin":"Tā men shì lǎo péng you.","english":"They are old friends","options":["They are old friends","They are new friends","They are classmates","They are colleagues"],"correctAnswer":3},
{"id":208,"sentence":"那个老人身体很好。","pinyin":"Nà gè lǎo rén shēn tǐ hěn hǎo.","english":"The old man is in good health","options":["The old man is in good health","The old man is sick","The old man is tired","The old man is angry"],"correctAnswer":1},
{"id":209,"sentence":"你的老师怎么样？","pinyin":"Nǐ de lǎo shī zěn me yàng?","english":"How is your teacher?","options":["How is your teacher?","How is your friend?","How is your father?","How is your mother?"],"correctAnswer":0},
{"id":210,"sentence":"下雨了。","pinyin":"Xià yǔ le.","english":"It's raining now","options":["It's raining now","It is sunny now","It is cloudy now","It is windy now"],"correctAnswer":0},
{"id":211,"sentence":"你累吗？","pinyin":"Nǐ lèi ma?","english":"Are you tired?","options":["Are you tired?","Are you happy?","Are you hungry?","Are you sick?"],"correctAnswer":3},
{"id":212,"sentence":"今天很冷。","pinyin":"Jīn tiān hěn lěng.","english":"It's cold today","options":["It's cold today","It's hot today","It's warm today","It's rainy today"],"correctAnswer":1},
{"id":213,"sentence":"我的护照在包里。","pinyin":"Wǒ de hù zhào zài bāo lǐ.","english":"My passport is in the bag","options":["My passport is in the bag","My passport is on the table","My passport is in the car","My passport is at home"],"correctAnswer":0},
{"id":214,"sentence":"公园里边有一个湖。","pinyin":"Gōng yuán lǐ bian yǒu yí gè hú.","english":"There is a lake in the park","options":["There is a lake in the park","There is a hill in the park","There is a river in the park","There is a tree in the park"],"correctAnswer":2},
{"id":215,"sentence":"我有两台电脑。","pinyin":"Wǒ yǒu liǎng tái diàn nǎo.","english":"I have two computers","options":["I have two computers","I have three computers","I have one computer","I have four computers"],"correctAnswer":3},
{"id":216,"sentence":"从零开始。","pinyin":"Cóng líng kāi shǐ.","english":"Start from zero","options":["Start from zero","Start from one","Start from ten","Start from five"],"correctAnswer":0},
{"id":217,"sentence":"我要六个饺子。","pinyin":"Wǒ yào liù gè jiǎo zi.","english":"I want six dumplings","options":["I want six dumplings","I want five dumplings","I want seven dumplings","I want four dumplings"],"correctAnswer":1},
{"id":218,"sentence":"你住在几楼？","pinyin":"Nǐ zhù zài jǐ lóu?","english":"Which floor do you live on?","options":["Which floor do you live on?","Which room do you live in?","Which building do you live in?","Which city do you live in?"],"correctAnswer":0},
{"id":219,"sentence":"我在楼上。","pinyin":"Wǒ zài lóu shàng.","english":"I'm upstairs","options":["I'm upstairs","I'm downstairs","I'm outside","I'm in the park"],"correctAnswer":1},
{"id":220,"sentence":"楼下有个超市。","pinyin":"Lóu xià yǒu gè chāo shì.","english":"There is a supermarket downstairs","options":["There is a supermarket downstairs","There is a bank downstairs","There is a restaurant downstairs","There is a park downstairs"],"correctAnswer":0},
{"id":221,"sentence":"淮海路在哪里？","pinyin":"Huái hǎi lù zài nǎ lǐ?","english":"Where is Huaihai Road?","options":["Where is Huaihai Road?","Where is Beijing Road?","Where is Nanjing Road?","Where is Shanghai Road?"],"correctAnswer":0},
{"id":222,"sentence":"请在路口停车。","pinyin":"Qǐng zài lù kǒu tíng chē.","english":"Please stop at the intersection","options":["Please stop at the intersection","Please stop at the traffic light","Please stop at the roundabout","Please stop at the school"],"correctAnswer":3},
{"id":223,"sentence":"他的车在路上坏了。","pinyin":"Tā de chē zài lù shang huài le.","english":"His car broke down on the road","options":["His car broke down on the road","His bike broke down on the road","His bus broke down on the road","His truck broke down on the road"],"correctAnswer":0},
{"id":224,"sentence":"我妈妈退休了。","pinyin":"Wǒ mā ma tuì xiū le.","english":"My mom is retired","options":["My mom is retired","My dad is retired","My mom is working","My mom is traveling"],"correctAnswer":0},
{"id":225,"sentence":"小心过马路。","pinyin":"Xiǎo xīn guò mǎ lù.","english":"Be careful crossing the road","options":["Be careful crossing the road","Be careful crossing the river","Be careful crossing the park","Be careful crossing the street"],"correctAnswer":3},
{"id":226,"sentence":"我马上付款。","pinyin":"Wǒ mǎ shàng fù kuǎn.","english":"I will pay right away","options":["I will pay right away","I will pay tomorrow","I will pay later","I will not pay"],"correctAnswer":0},
{"id":227,"sentence":"你要喝水吗？","pinyin":"Nǐ yào hē shuǐ ma?","english":"Do you want water?","options":["Do you want water?","Do you want juice?","Do you want tea?","Do you want coffee?"],"correctAnswer":0},
{"id":228,"sentence":"你要买什么？","pinyin":"Nǐ yào mǎi shén me?","english":"What do you want to buy?","options":["What do you want to buy?","What do you want to sell?","What do you want to eat?","What do you want to drink?"],"correctAnswer":0},
{"id":229,"sentence":"慢一点。","pinyin":"Màn yī diǎn.","english":"Slow down","options":["Slow down","Speed up","Go straight","Turn left"],"correctAnswer":1},
{"id":230,"sentence":"你忙吗？","pinyin":"Nǐ máng ma?","english":"Are you busy?","options":["Are you busy?","Are you free?","Are you tired?","Are you sleepy?"],"correctAnswer":0},
{"id":231,"sentence":"这杯茶八块五毛。","pinyin":"Zhè bēi chá bā kuài wǔ máo.","english":"This cup of tea costs eight yuan and fifty cents","options":["This cup of tea costs eight yuan and fifty cents","This cup of tea costs ten yuan","This cup of tea costs five yuan","This cup of tea costs nine yuan"],"correctAnswer":0},
{"id":232,"sentence":"他没吸烟。","pinyin":"Tā méi xī yān.","english":"He didn't smoke","options":["He didn't smoke","He smoked","He drinks","He eats"],"correctAnswer":1},
{"id":233,"sentence":"没关系。","pinyin":"Méi guān xi.","english":"It doesn't matter","options":["It doesn't matter","It matters","Be careful","Ignore it"],"correctAnswer":0},
{"id":234,"sentence":"没什么。","pinyin":"Méi shén me.","english":"It's nothing","options":["It's nothing","It's important","It's something","It's urgent"],"correctAnswer":0},
{"id":235,"sentence":"没事儿。","pinyin":"Méi shìr.","english":"It's okay / It's all right","options":["It's okay / It's all right","It's bad","It's wrong","It's urgent"],"correctAnswer":1},
{"id":236,"sentence":"这里没有超市。","pinyin":"Zhè lǐ méi yǒu chāo shì.","english":"There is no supermarket here","options":["There is no supermarket here","There is a supermarket here","There is a restaurant here","There is a bank here"],"correctAnswer":0},
{"id":237,"sentence":"我妹妹八岁了。","pinyin":"Wǒ mèi mei bā suì le.","english":"My younger sister is eight years old","options":["My younger sister is eight years old","My younger sister is nine years old","My younger sister is seven years old","My younger sister is ten years old"],"correctAnswer":0},
{"id":238,"sentence":"你锁门了吗？","pinyin":"Nǐ suǒ mén le ma?","english":"Did you lock the door?","options":["Did you lock the door?","Did you open the door?","Did you close the window?","Did you open the window?"],"correctAnswer":0},
{"id":239,"sentence":"别在门口外面停车。","pinyin":"Bié zài mén kǒu wài miàn tíng chē.","english":"Don't park outside the doorway","options":["Don't park outside the doorway","Don't park inside","Don't park on the street","Don't park in the park"],"correctAnswer":1},
{"id":240,"sentence":"门票多少钱？","pinyin":"Mén piào duō shao qián?","english":"How much is the ticket?","options":["How much is the ticket?","How much is the food?","How much is the drink?","How much is the pen?"],"correctAnswer":0},
{"id":241,"sentence":"我喜欢和朋友们一起聊天。","pinyin":"Wǒ xǐ huan hé péng you men yī qǐ liáo tiān.","english":"I like to chat with friends","options":["I like to chat with friends","I like to study with friends","I like to eat with friends","I like to sleep with friends"],"correctAnswer":0},
{"id":242,"sentence":"他吃了三碗米饭。","pinyin":"Tā chī le sān wǎn mǐ fàn.","english":"He ate three bowls of rice","options":["He ate three bowls of rice","He ate two bowls of rice","He ate four bowls of rice","He ate one bowl of rice"],"correctAnswer":0},
{"id":243,"sentence":"你会烤面包吗？","pinyin":"Nǐ huì kǎo miàn bāo ma?","english":"Can you bake bread?","options":["Can you bake bread?","Can you fry bread?","Can you boil bread?","Can you eat bread?"],"correctAnswer":0},
{"id":244,"sentence":"你想吃面条儿吗？","pinyin":"Nǐ xiǎng chī miàn tiáor ma?","english":"Do you want some noodles?","options":["Do you want some noodles?","Do you want some rice?","Do you want some bread?","Do you want some cake?"],"correctAnswer":0},
{"id":245,"sentence":"你叫什么名字？","pinyin":"Nǐ jiào shén me míng zi?","english":"What's your name?","options":["What's your name?","Who are you?","How old are you?","Where do you live?"],"correctAnswer":0},
{"id":246,"sentence":"我不明白。","pinyin":"Wǒ bù míng bai.","english":"I don't understand","options":["I don't understand","I understand","I know","I remember"],"correctAnswer":0},
{"id":247,"sentence":"他明年结婚。","pinyin":"Tā míng nián jié hūn.","english":"He is getting married next year","options":["He is getting married next year","He got married last year","He is divorcing next year","He is traveling next year"],"correctAnswer":0},
{"id":248,"sentence":"明天见。","pinyin":"Míng tiān jiàn.","english":"See you tomorrow","options":["See you tomorrow","See you today","See you yesterday","See you later"],"correctAnswer":3},
{"id":249,"sentence":"你拿护照了吗？","pinyin":"Nǐ ná hù zhào le ma?","english":"Did you take your passport?","options":["Did you take your passport?","Did you forget your passport?","Did you lose your passport?","Did you find your passport?"],"correctAnswer":0},
{"id":250,"sentence":"你要哪个？","pinyin":"Nǐ yào nǎ gè?","english":"Which one do you want?","options":["Which one do you want?","Which one do you need?","Which one do you like?","Which one do you choose?"],"correctAnswer":2},
{"id":251,"sentence":"你在哪里？","pinyin":"Nǐ zài nǎ lǐ?","english":"Where are you?","options":["Where are you?","Where is he?","Where is she?","Where is it?"],"correctAnswer":0},
{"id":252,"sentence":"你住在哪儿？","pinyin":"Nǐ zhù zài nǎr?","english":"Where do you live?","options":["Where do you live?","Where do you work?","Where do you study?","Where do you play?"],"correctAnswer":0},
{"id":253,"sentence":"哪些是你的？","pinyin":"Nǎ xiē shì nǐ de?","english":"Which ones are yours?","options":["Which ones are yours?","Which ones are mine?","Which ones are theirs?","Which ones are ours?"],"correctAnswer":0},
{"id":254,"sentence":"那是什么？","pinyin":"Nà shì shén me?","english":"What's that?","options":["What's that?","What's this?","Who is that?","Who is this?"],"correctAnswer":0},
{"id":255,"sentence":"图书馆在那边。","pinyin":"Tú shū guǎn zài nà bian.","english":"The library is over there","options":["The library is over there","The library is here","The library is upstairs","The library is downstairs"],"correctAnswer":0},
{"id":256,"sentence":"那里的天气怎么样？","pinyin":"Nà lǐ de tiān qì zěn me yàng?","english":"What's the weather like there?","options":["What's the weather like there?","What's the temperature?","Is it raining?","Is it sunny?"],"correctAnswer":0},
{"id":257,"sentence":"那儿的甜点很好吃。","pinyin":"Nàr de tián diǎn hěn hǎo chī.","english":"The desserts there are delicious","options":["The desserts there are delicious","The desserts there are bad","The desserts here are delicious","The desserts here are bad"],"correctAnswer":0},
{"id":258,"sentence":"那些甜点我都喜欢。","pinyin":"Nà xiē tián diǎn wǒ dōu xǐ huan.","english":"I like all those desserts","options":["I like all those desserts","I like none of the desserts","I like only one dessert","I like a few desserts"],"correctAnswer":0},
{"id":259,"sentence":"你喜欢喝奶茶？","pinyin":"Nǐ xǐ huan hē nǎi chá?","english":"Do you like to drink milk tea?","options":["Do you like to drink milk tea?","Do you like to drink coffee?","Do you like to drink tea?","Do you like to drink juice?"],"correctAnswer":0},
{"id":260,"sentence":"他是由奶奶带大的。","pinyin":"Tā shì yóu nǎi nai dài dà de.","english":"He was brought up by his grandma","options":["He was brought up by his grandma","He was brought up by his parents","He was brought up by his uncle","He was brought up by his teacher"],"correctAnswer":0},

{"id":261,"sentence":"医院里男护士很少。","pinyin":"Yī yuàn lǐ nán hù shì hěn shǎo.","english":"There are very few male nurses in the hospital","options":["There are very few male nurses in the hospital","There are many male nurses in the hospital","There are no nurses in the hospital","There are many doctors in the hospital"],"correctAnswer":0},
{"id":262,"sentence":"那个男孩儿真可爱。","pinyin":"Nà gè nán háir zhēn kě ài.","english":"That boy is so cute","options":["That boy is so cute","That boy is tall","That boy is funny","That boy is smart"],"correctAnswer":0},
{"id":263,"sentence":"她有男朋友吗？","pinyin":"Tā yǒu nán péng you ma?","english":"Does she have a boyfriend?","options":["Does she have a boyfriend?","Does she have a girlfriend?","Does she have a friend?","Does she have a brother?"],"correctAnswer":0},
{"id":264,"sentence":"那个男人是谁？","pinyin":"Nà gè nán rén shì shéi?","english":"Who is that man?","options":["Who is that man?","Who is that woman?","Who is this man?","Who is this woman?"],"correctAnswer":0},
{"id":265,"sentence":"那个男生很高。","pinyin":"Nà gè nán shēng hěn gāo.","english":"That boy is tall","options":["That boy is tall","That boy is short","That boy is old","That boy is young"],"correctAnswer":0},
{"id":266,"sentence":"他的房间朝南。","pinyin":"Tā de fáng jiān cháo nán.","english":"His room faces south","options":["His room faces south","His room faces north","His room faces east","His room faces west"],"correctAnswer":0},
{"id":267,"sentence":"超市在酒店南边。","pinyin":"Chāo shì zài jiǔ diàn nán biān.","english":"The supermarket is on the south side of the hotel","options":["The supermarket is on the south side of the hotel","The supermarket is on the north side","The supermarket is inside the hotel","The supermarket is far away"],"correctAnswer":0},
{"id":268,"sentence":"你觉得汉语难吗？","pinyin":"Nǐ jué de hàn yǔ nán ma?","english":"Do you think Chinese is difficult?","options":["Do you think Chinese is difficult?","Do you think Chinese is easy?","Do you like Chinese?","Do you speak Chinese?"],"correctAnswer":0},
{"id":269,"sentence":"我要喝咖啡，你呢？","pinyin":"Wǒ yào hē kā fēi, nǐ ne?","english":"I want coffee, how about you?","options":["I want coffee, how about you?","I want tea, how about you?","I don't want coffee, how about you?","I want juice, how about you?"],"correctAnswer":0},
{"id":270,"sentence":"他能来。","pinyin":"Tā néng lái.","english":"He can come","options":["He can come","He cannot come","He will come","He won't come"],"correctAnswer":0},
{"id":271,"sentence":"你有小孩吗？","pinyin":"Nǐ yǒu xiǎo hái ma?","english":"Do you have children?","options":["Do you have children?","Do you have pets?","Do you have friends?","Do you have siblings?"],"correctAnswer":0},
{"id":272,"sentence":"你们都是学生吗？","pinyin":"Nǐ men dōu shì xué sheng ma?","english":"Are you all students?","options":["Are you all students?","Are you all teachers?","Are you all friends?","Are you all workers?"],"correctAnswer":0},
{"id":273,"sentence":"他来中国五年了。","pinyin":"Tā lái zhōng guó wǔ nián le.","english":"He has been in China for five years","options":["He has been in China for five years","He came to China yesterday","He will come to China next year","He left China five years ago"],"correctAnswer":0},
{"id":274,"sentence":"您是哪位？","pinyin":"Nín shì nǎ wèi?","english":"Who are you?","options":["Who are you?","Where are you?","What is your name?","How old are you?"],"correctAnswer":0},
{"id":275,"sentence":"冰箱里没有牛奶了。","pinyin":"Bīng xiāng lǐ méi yǒu niú nǎi le.","english":"There is no milk in the fridge","options":["There is no milk in the fridge","There is milk in the fridge","There is juice in the fridge","There is water in the fridge"],"correctAnswer":0},
{"id":276,"sentence":"我们学校有很多女老师。","pinyin":"Wǒ men xué xiào yǒu hěn duō nǚ lǎo shī.","english":"There are many female teachers in our school","options":["There are many female teachers in our school","There are no female teachers","There are many male teachers","There are few teachers"],"correctAnswer":0},
{"id":277,"sentence":"你的女儿几岁了？","pinyin":"Nǐ de nǚ'ér jǐ suì le?","english":"How old is your daughter?","options":["How old is your daughter?","How old is your son?","How tall is your daughter?","How tall is your son?"],"correctAnswer":0},
{"id":278,"sentence":"你认识那个女孩儿吗？","pinyin":"Nǐ rèn shi nà gè nǚ háir ma?","english":"Do you know that girl?","options":["Do you know that girl?","Do you know that boy?","Do you like that girl?","Do you like that boy?"],"correctAnswer":0},
{"id":279,"sentence":"你有女朋友吗？","pinyin":"Nǐ yǒu nǚ péng you ma?","english":"Do you have a girlfriend?","options":["Do you have a girlfriend?","Do you have a boyfriend?","Do you have friends?","Do you have siblings?"],"correctAnswer":0},
{"id":280,"sentence":"那个女人是谁？","pinyin":"Nà gè nǚ rén shì shéi?","english":"Who is that woman?","options":["Who is that woman?","Who is that man?","Who is this woman?","Who is this man?"],"correctAnswer":0},
{"id":281,"sentence":"那个女生很漂亮。","pinyin":"Nà gè nǚ shēng hěn piào liang.","english":"That girl is beautiful","options":["That girl is beautiful","That girl is ugly","That girl is tall","That girl is short"],"correctAnswer":0},
{"id":282,"sentence":"咖啡馆在健身房旁边。","pinyin":"Kā fēi guǎn zài jiàn shēn fáng páng biān.","english":"The cafe is next to the gym","options":["The cafe is next to the gym","The cafe is far from the gym","The cafe is inside the gym","The cafe is behind the gym"],"correctAnswer":0},
{"id":283,"sentence":"他跑得快。","pinyin":"Tā pǎo de kuài.","english":"He runs fast","options":["He runs fast","He runs slowly","He walks fast","He walks slowly"],"correctAnswer":0},
{"id":284,"sentence":"这是我的朋友。","pinyin":"Zhè shì wǒ de péng you.","english":"This is my friend","options":["This is my friend","This is my teacher","This is my brother","This is my sister"],"correctAnswer":0},
{"id":285,"sentence":"你买票了吗？","pinyin":"Nǐ mǎi piào le ma?","english":"Have you bought the ticket?","options":["Have you bought the ticket?","Have you bought the food?","Have you bought the drink?","Have you bought the book?"],"correctAnswer":0},
{"id":286,"sentence":"我要休息七天。","pinyin":"Wǒ yào xiū xi qī tiān.","english":"I'm taking seven days off","options":["I'm taking seven days off","I'm taking five days off","I'm taking ten days off","I'm taking three days off"],"correctAnswer":0},
{"id":287,"sentence":"我明天要早起。","pinyin":"Wǒ míng tiān yào zǎo qǐ.","english":"I'm going to get up early tomorrow","options":["I'm going to get up early tomorrow","I'm going to sleep late tomorrow","I'm going to get up late tomorrow","I'm going to sleep early tomorrow"],"correctAnswer":0},
{"id":288,"sentence":"你通常几点起床？","pinyin":"Nǐ tōng cháng jǐ diǎn qǐ chuáng?","english":"What time do you usually get up?","options":["What time do you usually get up?","What time do you usually sleep?","What time do you usually eat?","What time do you usually go to school?"],"correctAnswer":0},
{"id":289,"sentence":"快起来！已经十一点了。","pinyin":"Kuài qǐ lái! Yǐ jīng shí yī diǎn le.","english":"Get up quickly! It's already eleven o'clock","options":["Get up quickly! It's already eleven o'clock","Go back to sleep! It's eleven o'clock","Eat breakfast! It's eleven o'clock","Leave home! It's eleven o'clock"],"correctAnswer":0},
{"id":290,"sentence":"马路上有很多汽车。","pinyin":"Mǎ lù shàng yǒu hěn duō qì chē.","english":"There are many cars on the road","options":["There are many cars on the road","There are no cars on the road","There are many bicycles on the road","There are many people on the road"],"correctAnswer":0},
{"id":291,"sentence":"你的包裹在门前。","pinyin":"Nǐ de bāo guǒ zài mén qián.","english":"Your package is in front of the door","options":["Your package is in front of the door","Your package is behind the door","Your package is inside the door","Your package is on the roof"],"correctAnswer":0},
{"id":292,"sentence":"酒店前边有一个公园。","pinyin":"Jiǔ diàn qián biān yǒu yī gè gōng yuán.","english":"There is a park in front of the hotel","options":["There is a park in front of the hotel","There is a park behind the hotel","There is a shop in front of the hotel","There is a bank in front of the hotel"],"correctAnswer":0},
{"id":293,"sentence":"我前天给他发了邮件。","pinyin":"Wǒ qián tiān gěi tā fā le yóu jiàn.","english":"I emailed him the day before yesterday","options":["I emailed him the day before yesterday","I emailed him yesterday","I will email him tomorrow","I emailed him last week"],"correctAnswer":0},
{"id":294,"sentence":"我没有钱。","pinyin":"Wǒ méi yǒu qián.","english":"I don't have money","options":["I don't have money","I have money","I have some coins","I have a credit card"],"correctAnswer":0},
{"id":295,"sentence":"我的钱包在车里。","pinyin":"Wǒ de qián bāo zài chē lǐ.","english":"My wallet is in the car","options":["My wallet is in the car","My wallet is at home","My wallet is in the bag","My wallet is on the desk"],"correctAnswer":0},
{"id":296,"sentence":"请回答。","pinyin":"Qǐng huí dá.","english":"Please answer","options":["Please answer","Please ask","Please wait","Please leave"],"correctAnswer":0},
{"id":297,"sentence":"我明天需要请假。","pinyin":"Wǒ míng tiān xū yào qǐng jià.","english":"I need to ask for leave tomorrow","options":["I need to ask for leave tomorrow","I need to work tomorrow","I need to study tomorrow","I need to go shopping tomorrow"],"correctAnswer":0},
{"id":298,"sentence":"请进。","pinyin":"Qǐng jìn.","english":"Please come in","options":["Please come in","Please go out","Please wait","Please sit"],"correctAnswer":0},
{"id":299,"sentence":"请问地铁站在哪里？","pinyin":"Qǐng wèn dì tiě zhàn zài nǎ lǐ?","english":"Excuse me, where is the subway station?","options":["Excuse me, where is the subway station?","Excuse me, where is the bus station?","Excuse me, where is the airport?","Excuse me, where is the train station?"],"correctAnswer":0},
{"id":300,"sentence":"请坐。","pinyin":"Qǐng zuò.","english":"Please have a seat","options":["Please have a seat","Please stand","Please leave","Please wait"],"correctAnswer":0},

{"id":301,"sentence":"这是什么球？","pinyin":"Zhè shì shén me qiú?","english":"What type of ball is this?","options":["What type of ball is this?","What is your name?","Where is the ball?","Who has the ball?"],"correctAnswer":0},
{"id":302,"sentence":"他去哪里了？","pinyin":"Tā qù nǎ lǐ le?","english":"Where did he go?","options":["Where did he go?","Where is he now?","Who is he?","When did he go?"],"correctAnswer":0},
{"id":303,"sentence":"他去年结婚了。","pinyin":"Tā qù nián jié hūn le.","english":"He got married last year","options":["He got married last year","He got married this year","He will get married next year","He is not married"],"correctAnswer":0},
{"id":304,"sentence":"太热了！","pinyin":"Tài rè le!","english":"It's too hot!","options":["It's too hot!","It's too cold!","It's perfect!","It's raining!"],"correctAnswer":0},
{"id":305,"sentence":"地铁上有很多人。","pinyin":"Dì tiě shàng yǒu hěn duō rén.","english":"There are lots of people on the metro","options":["There are lots of people on the metro","There is no one on the metro","The metro is empty","The metro is closed"],"correctAnswer":0},
{"id":306,"sentence":"你认识他吗？","pinyin":"Nǐ rèn shi tā ma?","english":"Do you know him?","options":["Do you know him?","Do you know her?","Do you like him?","Do you like her?"],"correctAnswer":0},
{"id":307,"sentence":"我是认真的。","pinyin":"Wǒ shì rèn zhēn de.","english":"I'm serious","options":["I'm serious","I'm joking","I'm confused","I'm tired"],"correctAnswer":0},
{"id":308,"sentence":"今天是十月一日。","pinyin":"Jīn tiān shì shí yuè yī rì.","english":"Today is the first day of October","options":["Today is the first day of October","Today is the first day of November","Today is October tenth","Today is September first"],"correctAnswer":0},
{"id":309,"sentence":"婚礼的日期定了吗？","pinyin":"Hūn lǐ de rì qī dìng le ma?","english":"Has the wedding date been set?","options":["Has the wedding date been set?","When is the wedding?","Is there a wedding?","Who is getting married?"],"correctAnswer":0},
{"id":310,"sentence":"你喜欢吃肉吗？","pinyin":"Nǐ xǐ huan chī ròu ma?","english":"Do you like to eat meat?","options":["Do you like to eat meat?","Do you like to eat vegetables?","Do you like to drink water?","Do you like fruits?"],"correctAnswer":0},
{"id":311,"sentence":"我有三台手机。","pinyin":"Wǒ yǒu sān tái shǒu jī.","english":"I have three cell phones","options":["I have three cell phones","I have two cell phones","I have one cell phone","I have four cell phones"],"correctAnswer":0},
{"id":312,"sentence":"这座山很美。","pinyin":"Zhè zuò shān hěn měi.","english":"This mountain is beautiful","options":["This mountain is beautiful","This mountain is small","This mountain is ugly","This mountain is high"],"correctAnswer":0},
{"id":313,"sentence":"你家附近有商场吗？","pinyin":"Nǐ jiā fù jìn yǒu shāng chǎng ma?","english":"Is there a shopping mall near your home?","options":["Is there a shopping mall near your home?","Is there a park near your home?","Is there a school near your home?","Is there a hospital near your home?"],"correctAnswer":0},
{"id":314,"sentence":"你想开一家商店吗？","pinyin":"Nǐ xiǎng kāi yī jiā shāng diàn ma?","english":"Do you want to open a shop?","options":["Do you want to open a shop?","Do you want to open a restaurant?","Do you want to open a school?","Do you want to open a hospital?"],"correctAnswer":0},
{"id":315,"sentence":"桌上有一些面包。","pinyin":"Zhuō shàng yǒu yī xiē miàn bāo.","english":"There is some bread on the table","options":["There is some bread on the table","There is some water on the table","There is some milk on the table","There is some fruit on the table"],"correctAnswer":0},
{"id":316,"sentence":"你通常几点上班？","pinyin":"Nǐ tōng cháng jǐ diǎn shàng bān?","english":"What time do you usually go to work?","options":["What time do you usually go to work?","What time do you go to school?","What time do you eat lunch?","What time do you wake up?"],"correctAnswer":0},
{"id":317,"sentence":"你的书在冰箱上边。","pinyin":"Nǐ de shū zài bīng xiāng shàng bian.","english":"Your book is on top of the fridge","options":["Your book is on top of the fridge","Your book is inside the fridge","Your book is under the fridge","Your book is next to the fridge"],"correctAnswer":0},
{"id":318,"sentence":"你上车了吗？","pinyin":"Nǐ shàng chē le ma?","english":"Did you get in the car?","options":["Did you get in the car?","Did you get off the car?","Did you buy a car?","Did you wash the car?"],"correctAnswer":0},
{"id":319,"sentence":"你上次吃中国菜是什么时候？","pinyin":"Nǐ shàng cì chī zhōng guó cài shì shén me shí hou?","english":"When was the last time you had Chinese food?","options":["When was the last time you had Chinese food?","When did you learn Chinese?","When did you go to China?","When did you cook Chinese food?"],"correctAnswer":0},
{"id":320,"sentence":"你今天要上课吗？","pinyin":"Nǐ jīn tiān yào shàng kè ma?","english":"Are you going to have a class today?","options":["Are you going to have a class today?","Are you going to work today?","Are you going shopping today?","Are you going to sleep today?"],"correctAnswer":0},
{"id":321,"sentence":"你每天上网吗？","pinyin":"Nǐ měi tiān shàng wǎng ma?","english":"Do you go online every day?","options":["Do you go online every day?","Do you read books every day?","Do you play games every day?","Do you exercise every day?"],"correctAnswer":0},
{"id":322,"sentence":"你明天上午有空吗？","pinyin":"Nǐ míng tiān shàng wǔ yǒu kòng ma?","english":"Are you free tomorrow morning?","options":["Are you free tomorrow morning?","Are you busy tomorrow morning?","Are you free tomorrow afternoon?","Are you free today morning?"],"correctAnswer":0},
{"id":323,"sentence":"你在哪里上学？","pinyin":"Nǐ zài nǎ lǐ shàng xué?","english":"Where do you go to school?","options":["Where do you go to school?","Where do you go to work?","Where is your school?","Where is your home?"],"correctAnswer":0},
{"id":324,"sentence":"请少放大蒜。","pinyin":"Qǐng shǎo fàng dà suàn.","english":"Please put less garlic","options":["Please put less garlic","Please put more garlic","Please don't put garlic","Please put garlic aside"],"correctAnswer":0},
{"id":325,"sentence":"谁在敲门？","pinyin":"Shéi zài qiāo mén?","english":"Who is knocking on the door?","options":["Who is knocking on the door?","Who is at the window?","Who is in the house?","Who is outside?"],"correctAnswer":0},
{"id":326,"sentence":"他身上有一只蜘蛛。","pinyin":"Tā shēn shang yǒu yī zhī zhī zhū.","english":"There is a spider on him (on his body)","options":["There is a spider on him (on his body)","There is a spider on the wall","There is a spider on the floor","There is a spider outside"],"correctAnswer":0},
{"id":327,"sentence":"你的身体怎么样？","pinyin":"Nǐ de shēn tǐ zěn me yàng?","english":"How is your body? (How is your health?)","options":["How is your body? (How is your health?)","How is your mood?","How is your family?","How is your house?"],"correctAnswer":0},
{"id":328,"sentence":"你想吃什么？","pinyin":"Nǐ xiǎng chī shén me?","english":"What do you want to eat?","options":["What do you want to eat?","What do you want to drink?","What do you want to buy?","What do you want to do?"],"correctAnswer":0},
{"id":329,"sentence":"他没生病。","pinyin":"Tā méi shēng bìng.","english":"He didn't get sick","options":["He didn't get sick","He got sick","He is healthy","He is tired"],"correctAnswer":0},
{"id":330,"sentence":"别生气。","pinyin":"Bié shēng qì.","english":"Don't get angry","options":["Don't get angry","Get angry","Be happy","Be sad"],"correctAnswer":0},

{"id":331,"sentence":"生日快乐！","pinyin":"Shēng rì kuài lè!","english":"Happy birthday!","options":["Happy birthday!","Merry Christmas!","Congratulations!","Good night!"],"correctAnswer":0},
{"id":332,"sentence":"你想休息十天吗？","pinyin":"Nǐ xiǎng xiū xi shí tiān ma?","english":"Do you want to take ten days off?","options":["Do you want to take ten days off?","Do you want to take five days off?","Do you want to take a week off?","Do you want to take a month off?"],"correctAnswer":0},
{"id":333,"sentence":"那个时候我不认识他。","pinyin":"Nà gè shí hou wǒ bù rèn shi tā.","english":"I didn't know him at that time","options":["I didn't know him at that time","I knew him at that time","I didn't see him at that time","I met him at that time"],"correctAnswer":0},
{"id":334,"sentence":"你有时间吗？","pinyin":"Nǐ yǒu shí jiān ma?","english":"Do you have time?","options":["Do you have time?","Do you have money?","Do you have friends?","Do you have food?"],"correctAnswer":0},
{"id":335,"sentence":"这件事很复杂。","pinyin":"Zhè jiàn shì hěn fù zá.","english":"This thing is complicated","options":["This thing is complicated","This thing is simple","This thing is easy","This thing is boring"],"correctAnswer":0},
{"id":336,"sentence":"我可以试一下鞋子吗？","pinyin":"Wǒ kě yǐ shì yí xià xié zi ma?","english":"Can I try on the shoes?","options":["Can I try on the shoes?","Can I buy the shoes?","Can I clean the shoes?","Can I repair the shoes?"],"correctAnswer":0},
{"id":337,"sentence":"你是学生吗？","pinyin":"Nǐ shì xué sheng ma?","english":"Are you a student?","options":["Are you a student?","Are you a teacher?","Are you a worker?","Are you a doctor?"],"correctAnswer":0},
{"id":338,"sentence":"他是不是老板？","pinyin":"Tā shì bú shì lǎo bǎn?","english":"Is he the boss?","options":["Is he the boss?","Is he a student?","Is he a teacher?","Is he a worker?"],"correctAnswer":0},
{"id":339,"sentence":"我要洗手。","pinyin":"Wǒ yào xǐ shǒu.","english":"I want to wash my hands","options":["I want to wash my hands","I want to wash my face","I want to take a shower","I want to wash my clothes"],"correctAnswer":0},
{"id":340,"sentence":"我的手机没电了。","pinyin":"Wǒ de shǒu jī méi diàn le.","english":"My cell phone is out of battery","options":["My cell phone is out of battery","My cell phone is new","My cell phone is lost","My cell phone is broken"],"correctAnswer":0},
{"id":341,"sentence":"你喜欢看什么书？","pinyin":"Nǐ xǐ huan kàn shén me shū?","english":"What type of books do you like to read?","options":["What type of books do you like to read?","What type of movies do you like?","What type of music do you like?","What type of food do you like?"],"correctAnswer":0},
{"id":342,"sentence":"你的书包里有什么？","pinyin":"Nǐ de shū bāo lǐ yǒu shén me?","english":"What's in your school bag?","options":["What's in your school bag?","What's on your desk?","What's in your pocket?","What's on the table?"],"correctAnswer":0},
{"id":343,"sentence":"这家书店营业二十四小时。","pinyin":"Zhè jiā shū diàn yíng yè èr shí sì xiǎo shí.","english":"The bookstore is open twenty-four hours","options":["The bookstore is open twenty-four hours","The bookstore is open twelve hours","The bookstore is closed","The bookstore opens tomorrow"],"correctAnswer":0},
{"id":344,"sentence":"这是什么树？","pinyin":"Zhè shì shén me shù?","english":"What type of tree is this?","options":["What type of tree is this?","What type of flower is this?","What type of plant is this?","What type of bush is this?"],"correctAnswer":0},
{"id":345,"sentence":"你每天喝几杯水？","pinyin":"Nǐ měi tiān hē jǐ bēi shuǐ?","english":"How many glasses of water do you drink per day?","options":["How many glasses of water do you drink per day?","How many cups of tea do you drink?","How many bottles of juice do you drink?","How many glasses of milk do you drink?"],"correctAnswer":0},
{"id":346,"sentence":"你最喜欢吃什么水果？","pinyin":"Nǐ zuì xǐ huan chī shén me shuǐ guǒ?","english":"What's your favorite fruit?","options":["What's your favorite fruit?","What's your favorite vegetable?","What's your favorite food?","What's your favorite drink?"],"correctAnswer":0},
{"id":347,"sentence":"你每天睡多少个小时？","pinyin":"Nǐ měi tiān shuì duō shao gè xiǎo shí?","english":"How many hours do you sleep per day?","options":["How many hours do you sleep per day?","How many hours do you study?","How many hours do you work?","How many hours do you play games?"],"correctAnswer":0},
{"id":348,"sentence":"你几点睡觉？","pinyin":"Nǐ jǐ diǎn shuì jiào?","english":"What time do you sleep?","options":["What time do you sleep?","What time do you wake up?","What time do you eat?","What time do you go to school?"],"correctAnswer":0},
{"id":349,"sentence":"你会说汉语吗？","pinyin":"Nǐ huì shuō hàn yǔ ma?","english":"Do you speak Chinese?","options":["Do you speak Chinese?","Do you speak English?","Do you speak Japanese?","Do you speak French?"],"correctAnswer":0},
{"id":350,"sentence":"别说话。","pinyin":"Bié shuō huà.","english":"Don't talk","options":["Don't talk","Talk now","Listen carefully","Speak loudly"],"correctAnswer":0},
{"id":351,"sentence":"他喝了四瓶可乐。","pinyin":"Tā hē le sì píng kě lè.","english":"He drank four bottles of coke","options":["He drank four bottles of coke","He drank two bottles of coke","He drank one bottle of coke","He didn't drink coke"],"correctAnswer":0},
{"id":352,"sentence":"你可以送给我吗？","pinyin":"Nǐ kě yǐ sòng gěi wǒ ma?","english":"Can you give it to me (as a gift)?","options":["Can you give it to me (as a gift)?","Can you sell it to me?","Can you take it away?","Can you borrow it?"],"correctAnswer":0},
{"id":353,"sentence":"我哥哥三十岁了。","pinyin":"Wǒ gē ge sān shí suì le.","english":"My elder brother is thirty years old","options":["My elder brother is thirty years old","My elder brother is twenty years old","My elder brother is forty years old","My elder brother is fifty years old"],"correctAnswer":0},
{"id":354,"sentence":"你讨厌他吗？","pinyin":"Nǐ tǎo yàn tā ma?","english":"Do you hate him?","options":["Do you hate him?","Do you love him?","Do you like him?","Do you know him?"],"correctAnswer":0},
{"id":355,"sentence":"他们是同学。","pinyin":"Tā men shì tóng xué.","english":"They are classmates","options":["They are classmates","They are brothers","They are friends","They are teachers"],"correctAnswer":0},
{"id":356,"sentence":"她是我女朋友。","pinyin":"Tā shì wǒ nǚ péng you.","english":"She is my girlfriend","options":["She is my girlfriend","She is my sister","She is my mother","She is my friend"],"correctAnswer":0},
{"id":357,"sentence":"她们是双胞胎。","pinyin":"Tā men shì shuāng bāo tāi.","english":"They (for females) are twins","options":["They (for females) are twins","They are friends","They are classmates","They are sisters"],"correctAnswer":0},
{"id":358,"sentence":"太小了。","pinyin":"Tài xiǎo le.","english":"It's too small","options":["It's too small","It's too big","It's perfect","It's beautiful"],"correctAnswer":0},
{"id":359,"sentence":"我要出差十天。","pinyin":"Wǒ yào chū chāi shí tiān.","english":"I'm going on a business trip for ten days","options":["I'm going on a business trip for ten days","I'm going on a holiday for ten days","I'm staying home for ten days","I'm traveling for five days"],"correctAnswer":0},
{"id":360,"sentence":"今天天气真好。","pinyin":"Jīn tiān tiān qì zhēn hǎo.","english":"The weather is so nice today","options":["The weather is so nice today","The weather is bad today","It's raining today","It's cold today"],"correctAnswer":0},
{"id":361,"sentence":"你喜欢听中文歌吗？","pinyin":"Nǐ xǐ huan tīng zhōng wén gē ma?","english":"Do you like to listen to Chinese songs?","options":["Do you like to listen to Chinese songs?","Do you like to listen to English songs?","Do you like to sing songs?","Do you like to play music?"],"correctAnswer":0},
{"id":362,"sentence":"你听到了吗？","pinyin":"Nǐ tīng dào le ma?","english":"Did you hear it?","options":["Did you hear it?","Did you see it?","Did you touch it?","Did you smell it?"],"correctAnswer":0},
{"id":363,"sentence":"你听见雷声了吗？","pinyin":"Nǐ tīng jiàn léi shēng le ma?","english":"Did you hear the thunder?","options":["Did you hear the thunder?","Did you hear the rain?","Did you hear the wind?","Did you hear the bell?"],"correctAnswer":0},
{"id":364,"sentence":"我们要听写生词。","pinyin":"Wǒ men yào tīng xiě shēng cí.","english":"We are going to dictate the new words","options":["We are going to dictate the new words","We are going to read the new words","We are going to write a story","We are going to sing a song"],"correctAnswer":0},
{"id":365,"sentence":"她是我的大学同学。","pinyin":"Tā shì wǒ de dà xué tóng xué.","english":"She is my college classmate","options":["She is my college classmate","She is my sister","She is my teacher","She is my neighbor"],"correctAnswer":0},
{"id":366,"sentence":"图书馆在哪里？","pinyin":"Tú shū guǎn zài nǎ lǐ?","english":"Where is the library?","options":["Where is the library?","Where is the bookstore?","Where is the school?","Where is the park?"],"correctAnswer":0},
{"id":367,"sentence":"你的披萨在门外。","pinyin":"Nǐ de pī sà zài mén wài.","english":"Your pizza is outside the door","options":["Your pizza is outside the door","Your pizza is inside","Your pizza is on the table","Your pizza is in the fridge"],"correctAnswer":0},
{"id":368,"sentence":"外边风很大。","pinyin":"Wài biān fēng hěn dà.","english":"It's very windy outside","options":["It's very windy outside","It's sunny outside","It's raining outside","It's snowing outside"],"correctAnswer":0},
{"id":369,"sentence":"你喜欢看外国电影吗？","pinyin":"Nǐ xǐ huan kàn wài guó diàn yǐng ma?","english":"Do you like to watch foreign movies?","options":["Do you like to watch foreign movies?","Do you like to watch Chinese movies?","Do you like to watch TV shows?","Do you like to watch cartoons?"],"correctAnswer":0},
{"id":370,"sentence":"你想学什么外语？","pinyin":"Nǐ xiǎng xué shén me wài yǔ?","english":"What foreign language do you want to learn?","options":["What foreign language do you want to learn?","What subject do you want to learn?","What sport do you want to learn?","What hobby do you want to learn?"],"correctAnswer":0},
{"id":371,"sentence":"我们一起玩儿吧！","pinyin":"Wǒ men yī qǐ wánr ba!","english":"Let's play together!","options":["Let's play together!","Let's study together!","Let's eat together!","Let's watch TV together!"],"correctAnswer":0},
{"id":372,"sentence":"太晚了。","pinyin":"Tài wǎn le.","english":"It's too late","options":["It's too late","It's too early","It's just right","It's morning"],"correctAnswer":0},
{"id":373,"sentence":"晚饭做好了。","pinyin":"Wǎn fàn zuò hǎo le.","english":"Dinner is ready","options":["Dinner is ready","Lunch is ready","Breakfast is ready","Snack is ready"],"correctAnswer":0},
{"id":374,"sentence":"晚上好！","pinyin":"Wǎn shang hǎo!","english":"Good evening!","options":["Good evening!","Good morning!","Good afternoon!","Good night!"],"correctAnswer":0},
{"id":375,"sentence":"我们是在网上认识的。","pinyin":"Wǒ men shì zài wǎng shàng rèn shi de.","english":"We met online","options":["We met online","We met in person","We met at school","We met at work"],"correctAnswer":0},
{"id":376,"sentence":"他有很多网友。","pinyin":"Tā yǒu hěn duō wǎng yǒu.","english":"He has many friends on the internet","options":["He has many friends on the internet","He has many friends in real life","He has many relatives","He has many classmates"],"correctAnswer":0},
{"id":377,"sentence":"别忘了买面包。","pinyin":"Bié wàng le mǎi miàn bāo.","english":"Don't forget to buy bread","options":["Don't forget to buy bread","Don't forget to buy milk","Don't forget to buy fruit","Don't forget to buy water"],"correctAnswer":0},
{"id":378,"sentence":"我不会忘记的。","pinyin":"Wǒ bù huì wàng jì de.","english":"I won't forget","options":["I won't forget","I will forget","I might forget","I forgot"],"correctAnswer":0},
{"id":379,"sentence":"你可以问老师。","pinyin":"Nǐ kě yǐ wèn lǎo shī.","english":"You can ask the teacher","options":["You can ask the teacher","You can ask a friend","You can ask the principal","You can ask your parent"],"correctAnswer":0},
{"id":380,"sentence":"你爱我吗？","pinyin":"Nǐ ài wǒ ma?","english":"Do you love me?","options":["Do you love me?","Do you like me?","Do you hate me?","Do you know me?"],"correctAnswer":0},

{"id":381,"sentence":"我们会说中文。","pinyin":"Wǒ men dōu shuō zhōng wén.","english":"We can speak Chinese.","options":["We can speak Chinese","We can speak English","We can speak French","We can speak Japanese"],"correctAnswer":0},
{"id":382,"sentence":"他学中文五年了。","pinyin":"Tā xué zhōng wén wǔ nián le.","english":"He has been studying Chinese for five years.","options":["He has been studying Chinese for five years","He has been studying Chinese for three years","He has been studying Chinese for ten years","He has been studying Chinese for one year"],"correctAnswer":0},
{"id":383,"sentence":"你吃午饭了吗？","pinyin":"Nǐ chī wǔ fàn le ma?","english":"Did you have lunch?","options":["Did you have lunch?","Did you have breakfast?","Did you have dinner?","Are you having lunch?"],"correctAnswer":0},
{"id":384,"sentence":"他的房子朝西。","pinyin":"Tā de fáng zi cháo xī.","english":"His house faces west.","options":["His house faces west","His house faces east","His house faces south","His house faces north"],"correctAnswer":0},
{"id":385,"sentence":"医院在学校西边。","pinyin":"Yī yuàn zài xué xiào xī bian.","english":"The hospital is on the west side of the school.","options":["The hospital is on the west side of the school","The hospital is on the east side of the school","The hospital is on the south side of the school","The hospital is on the north side of the school"],"correctAnswer":0},
{"id":386,"sentence":"你可以帮我洗车吗？","pinyin":"Nǐ kě yǐ bāng wǒ xǐ chē ma?","english":"Can you wash my car for me?","options":["Can you wash my car for me?","Can you wash my bike for me?","Can you clean my room for me?","Can you cook for me?"],"correctAnswer":0},
{"id":387,"sentence":"洗手间在二楼。","pinyin":"Xǐ shǒu jiān zài èr lóu.","english":"The washroom is on the second floor.","options":["The washroom is on the second floor","The washroom is on the first floor","The washroom is outside","The washroom is on the third floor"],"correctAnswer":0},
{"id":388,"sentence":"你喜欢吃什么？","pinyin":"Nǐ xǐ huan chī shén me?","english":"What do you like to eat?","options":["What do you like to eat?","What do you like to drink?","What is your favorite color?","What is your favorite sport?"],"correctAnswer":0},
{"id":389,"sentence":"你下飞机了吗？","pinyin":"Nǐ xià fēi jī le ma?","english":"Did you get off the plane?","options":["Did you get off the plane?","Did you get on the plane?","Did you leave the airport?","Did you enter the airport?"],"correctAnswer":0},
{"id":390,"sentence":"你几点下班？","pinyin":"Nǐ jǐ diǎn xià bān?","english":"What time do you get off work?","options":["What time do you get off work?","What time do you start work?","What time do you finish class?","What time do you wake up?"],"correctAnswer":0},
{"id":391,"sentence":"你的笔在桌子下边。","pinyin":"Nǐ de bǐ zài zhuō zi xià bian.","english":"Your pen is under the table.","options":["Your pen is under the table","Your pen is on the table","Your pen is next to the table","Your pen is in the drawer"],"correctAnswer":0},
{"id":392,"sentence":"我在下一个路口下车。","pinyin":"Wǒ zài xià yí gè lù kǒu xià chē.","english":"I get off at the next intersection.","options":["I get off at the next intersection","I get on at the next intersection","I get off at the last stop","I get on at the last stop"],"correctAnswer":0},
{"id":393,"sentence":"下次见！","pinyin":"Xià cì jiàn!","english":"See you next time!","options":["See you next time!","Goodbye!","Hello!","See you yesterday!"],"correctAnswer":0},
{"id":394,"sentence":"你今天几点下课？","pinyin":"Nǐ jīn tiān jǐ diǎn xià kè?","english":"What time do you finish class today?","options":["What time do you finish class today?","What time do you start class today?","What time is lunch today?","What time do you wake up today?"],"correctAnswer":0},
{"id":395,"sentence":"你下午有空吗？","pinyin":"Nǐ xià wǔ yǒu kòng ma?","english":"Are you free this afternoon?","options":["Are you free this afternoon?","Are you free this morning?","Are you free this evening?","Are you busy this afternoon?"],"correctAnswer":0},
{"id":396,"sentence":"明天会下雨。","pinyin":"Míng tiān huì xià yǔ.","english":"It will rain tomorrow.","options":["It will rain tomorrow","It will snow tomorrow","It will be sunny tomorrow","It will be cloudy tomorrow"],"correctAnswer":0},
{"id":397,"sentence":"我们先做作业，再看电视。","pinyin":"Wǒ men xiān zuò zuò yè, zài kàn diàn shì.","english":"We do our homework first and then watch TV.","options":["We do our homework first and then watch TV","We watch TV first and then do homework","We sleep first and then watch TV","We eat first and then do homework"],"correctAnswer":0},
{"id":398,"sentence":"你是高先生吗？","pinyin":"Nǐ shì gāo xiān sheng ma?","english":"Are you Mr. Gao?","options":["Are you Mr. Gao?","Are you Mr. Wang?","Are you Mr. Li?","Are you Mr. Chen?"],"correctAnswer":0},
{"id":399,"sentence":"现在几点？","pinyin":"Xiàn zài jǐ diǎn?","english":"What time is it now?","options":["What time is it now?","What time was it yesterday?","What time is lunch?","What time is your class?"],"correctAnswer":0},
{"id":400,"sentence":"我需要想一下。","pinyin":"Wǒ xū yào xiǎng yí xià.","english":"I need to think about it.","options":["I need to think about it","I need to do it now","I need to eat now","I need to sleep now"],"correctAnswer":0},


{"id":401,"sentence":"我的家很小。","pinyin":"Wǒ de jiā hěn xiǎo.","english":"My home is small.","options":["My home is small","My home is big","My home is beautiful","My home is new"],"correctAnswer":0},
{"id":402,"sentence":"你有小孩儿吗？","pinyin":"Nǐ yǒu xiǎo háir ma?","english":"Do you have children?","options":["Do you have children?","Do you have pets?","Do you have siblings?","Do you have friends?"],"correctAnswer":0},
{"id":403,"sentence":"这是赵小姐。","pinyin":"Zhè shì Zhào xiǎo jiě.","english":"This is Miss Zhao.","options":["This is Miss Zhao","This is Mrs. Zhao","This is Mr. Zhao","This is Ms. Wang"],"correctAnswer":0},
{"id":404,"sentence":"那个小朋友很可爱。","pinyin":"Nà gè xiǎo péng you hěn kě ài.","english":"That kid is so cute.","options":["That kid is so cute","That kid is very tall","That kid is naughty","That kid is sad"],"correctAnswer":0},
{"id":405,"sentence":"你每天工作几个小时？","pinyin":"Nǐ měi tiān gōng zuò jǐ gè xiǎo shí?","english":"How many hours do you work per day?","options":["How many hours do you work per day","How many hours do you sleep","How many hours do you study","How many hours do you play"],"correctAnswer":0},
{"id":406,"sentence":"她是小学老师。","pinyin":"Tā shì xiǎo xué lǎo shī.","english":"She is an elementary school teacher.","options":["She is an elementary school teacher","She is a middle school teacher","She is a college professor","She is a student"],"correctAnswer":0},
{"id":407,"sentence":"那个小学生很高。","pinyin":"Nà gè xiǎo xué shēng hěn gāo.","english":"That elementary school student is tall.","options":["That elementary school student is tall","That elementary school student is short","That elementary school student is smart","That elementary school student is young"],"correctAnswer":0},
{"id":408,"sentence":"他在笑什么？","pinyin":"Tā zài xiào shén me?","english":"What is he laughing at?","options":["What is he laughing at","Why is he crying","What is he doing","Why is he sleeping"],"correctAnswer":0},
{"id":409,"sentence":"你会写汉字吗？","pinyin":"Nǐ huì xiě hàn zì ma?","english":"Can you write Chinese characters?","options":["Can you write Chinese characters","Can you read Chinese characters","Can you speak Chinese","Can you draw pictures"],"correctAnswer":0},
{"id":410,"sentence":"谢谢！","pinyin":"Xiè xie!","english":"Thank you!","options":["Thank you!","You're welcome!","Sorry!","Goodbye!"],"correctAnswer":0},
{"id":411,"sentence":"这是你的新手机吗？","pinyin":"Zhè shì nǐ de xīn shǒu jī ma?","english":"Is this your new phone?","options":["Is this your new phone","Is this your old phone","Is this your friend's phone","Is this a broken phone"],"correctAnswer":0},
{"id":412,"sentence":"新年快乐！","pinyin":"Xīn nián kuài lè!","english":"Happy New Year!","options":["Happy New Year!","Merry Christmas!","Happy Birthday!","Good Night!"],"correctAnswer":0},
{"id":413,"sentence":"我下个星期要搬家。","pinyin":"Wǒ xià gè xīng qī yào bān jiā.","english":"I'm moving next week.","options":["I'm moving next week","I'm traveling next week","I'm staying home next week","I'm working next week"],"correctAnswer":0},
{"id":414,"sentence":"我这个星期日有中文课。","pinyin":"Wǒ zhè gè xīng qī rì yǒu zhōng wén kè.","english":"I have Chinese class this Sunday.","options":["I have Chinese class this Sunday","I have math class this Sunday","I have English class this Sunday","I have no class this Sunday"],"correctAnswer":0},
{"id":415,"sentence":"你这个星期天有空吗？","pinyin":"Nǐ zhè gè xīng qī tiān yǒu kòng ma?","english":"Are you free this Sunday?","options":["Are you free this Sunday","Are you busy this Sunday","Are you traveling this Sunday","Are you studying this Sunday"],"correctAnswer":0},
{"id":416,"sentence":"行吗？","pinyin":"Xíng ma?","english":"Is it OK?","options":["Is it OK?","Is it not OK?","Can I go?","Should I wait?"],"correctAnswer":0},
{"id":417,"sentence":"你要休息吗？","pinyin":"Nǐ yào xiū xi ma?","english":"Do you want to rest?","options":["Do you want to rest?","Do you want to work?","Do you want to eat?","Do you want to study?"],"correctAnswer":0},
{"id":418,"sentence":"你学中文多久了？","pinyin":"Nǐ xué zhōng wén duō jiǔ le?","english":"How long have you been studying Chinese?","options":["How long have you been studying Chinese","How long have you been learning English","How long have you been working","How long have you been traveling"],"correctAnswer":0},
{"id":419,"sentence":"他是一个好学生。","pinyin":"Tā shì yí gè hǎo xué sheng.","english":"He is a good student.","options":["He is a good student","He is a bad student","He is a smart student","He is a tall student"],"correctAnswer":0},
{"id":420,"sentence":"你想学习吗？","pinyin":"Nǐ xiǎng xué xí ma?","english":"Do you want to study?","options":["Do you want to study?","Do you want to play?","Do you want to eat?","Do you want to sleep?"],"correctAnswer":0},

{"id":421,"sentence":"这个学校怎么样？","pinyin":"Zhè gè xué xiào zěn me yàng?","english":"How is this school?","options":["How is this school?","How is this teacher?","How is this student?","How is this city?"],"correctAnswer":0},
{"id":422,"sentence":"这个学院大吗？","pinyin":"Zhè gè xué yuàn dà ma?","english":"Is this college big?","options":["Is this college big?","Is this college small?","Is this school big?","Is this school small?"],"correctAnswer":0},
{"id":423,"sentence":"你要吃巧克力吗？","pinyin":"Nǐ yào chī qiǎo kè lì ma?","english":"Do you want some chocolate?","options":["Do you want some chocolate?","Do you want some candy?","Do you want some cake?","Do you want some fruit?"],"correctAnswer":0},
{"id":424,"sentence":"我爷爷退休了。","pinyin":"Wǒ yé ye tuì xiū le.","english":"My grandpa is retired.","options":["My grandpa is retired","My grandpa is working","My grandpa is traveling","My grandpa is sick"],"correctAnswer":0},
{"id":425,"sentence":"我也喜欢跳舞。","pinyin":"Wǒ yě xǐ huan tiào wǔ.","english":"I also like to dance.","options":["I also like to dance","I like to sing","I like to play sports","I like to read"],"correctAnswer":0},
{"id":426,"sentence":"第几页？","pinyin":"Dì jǐ yè?","english":"Which page?","options":["Which page?","What chapter?","Which book?","What line?"],"correctAnswer":0},
{"id":427,"sentence":"利息率是百分之一。","pinyin":"Lì xī lǜ shì bǎi fēn zhī yī.","english":"The interest rate is one percent.","options":["The interest rate is one percent","The interest rate is ten percent","The interest rate is five percent","The interest rate is zero percent"],"correctAnswer":0},
{"id":428,"sentence":"这件衣服的质量很好。","pinyin":"Zhè jiàn yī fu de zhì liàng hěn hǎo.","english":"The quality of these clothes is good.","options":["The quality of these clothes is good","The quality of these clothes is bad","The clothes are expensive","The clothes are small"],"correctAnswer":0},
{"id":429,"sentence":"他是医生。","pinyin":"Tā shì yī shēng.","english":"He is a doctor.","options":["He is a doctor","He is a nurse","He is a teacher","He is a student"],"correctAnswer":0},
{"id":430,"sentence":"附近有医院吗？","pinyin":"Fù jìn yǒu yī yuàn ma?","english":"Is there a hospital nearby?","options":["Is there a hospital nearby?","Is there a school nearby?","Is there a shop nearby?","Is there a park nearby?"],"correctAnswer":0},
{"id":431,"sentence":"这是你的一半。","pinyin":"Zhè shì nǐ de yí bàn.","english":"This is your half.","options":["This is your half","This is your whole","This is your share","This is your part"],"correctAnswer":0},
{"id":432,"sentence":"请等一会儿。","pinyin":"Qǐng děng yí huìr.","english":"Please wait a moment.","options":["Please wait a moment","Please hurry","Please come in","Please go out"],"correctAnswer":0},
{"id":433,"sentence":"我们一块儿玩吧！","pinyin":"Wǒ men yí kuàir wán ba!","english":"Let's play together!","options":["Let's play together","Let's eat together","Let's study together","Let's walk together"],"correctAnswer":0},
{"id":434,"sentence":"你可以照顾一下儿宝宝吗？","pinyin":"Nǐ kě yǐ zhào gù yí xiàr bǎo bǎo ma?","english":"Can you look after the baby for a bit?","options":["Can you look after the baby for a bit?","Can you feed the baby?","Can you play with the baby?","Can you wash the baby?"],"correctAnswer":0},
{"id":435,"sentence":"他们一样高。","pinyin":"Tā men yí yàng gāo.","english":"They are the same height.","options":["They are the same height","They are different heights","They are tall","They are short"],"correctAnswer":0},
{"id":436,"sentence":"她的头发一边长，一边短。","pinyin":"Tā de tóu fa yì biān cháng, yì biān duǎn.","english":"Her hair is long on one side and short on the other.","options":["Her hair is long on one side and short on the other","Her hair is short","Her hair is long","Her hair is curly"],"correctAnswer":0},
{"id":437,"sentence":"我会说一点儿中文。","pinyin":"Wǒ huì shuō yī diǎnr zhōng wén.","english":"I can speak a little bit Chinese.","options":["I can speak a little bit Chinese","I can speak fluently","I cannot speak","I can write Chinese"],"correctAnswer":0},
{"id":438,"sentence":"我们一起去旅行吧！","pinyin":"Wǒ men yì qǐ qù lǚ xíng ba!","english":"Let's travel together!","options":["Let's travel together","Let's eat together","Let's study together","Let's work together"],"correctAnswer":0},
{"id":439,"sentence":"他买了一些衣服。","pinyin":"Tā mǎi le yì xiē yī fu.","english":"He bought some clothes.","options":["He bought some clothes","He bought some food","He bought some books","He bought some toys"],"correctAnswer":0},
{"id":440,"sentence":"你会用筷子吗？","pinyin":"Nǐ huì yòng kuài zi ma?","english":"Can you use chopsticks?","options":["Can you use chopsticks?","Can you use a fork?","Can you use a spoon?","Can you use a knife?"],"correctAnswer":0},
{"id":441,"sentence":"我有一个哥哥。","pinyin":"Wǒ yǒu yí gè gē ge.","english":"I have an elder brother.","options":["I have an elder brother","I have a younger brother","I have a sister","I have no siblings"],"correctAnswer":0},
{"id":442,"sentence":"有的人喜欢米饭，有的人喜欢面条。","pinyin":"Yǒu de rén xǐ huan mǐ fàn, yǒu de rén xǐ huan miàn tiáo.","english":"Some people like rice, some people like noodles.","options":["Some people like rice, some people like noodles","Some people like rice only","Some people like noodles only","Some people like bread"],"correctAnswer":0},
{"id":443,"sentence":"她很有名。","pinyin":"Tā hěn yǒu míng.","english":"She is famous.","options":["She is famous","She is unknown","She is smart","She is tall"],"correctAnswer":0},
{"id":444,"sentence":"我有时候在家做饭。","pinyin":"Wǒ yǒu shí hou zài jiā zuò fàn.","english":"I sometimes cook at home.","options":["I sometimes cook at home","I always cook at home","I never cook at home","I often eat out"],"correctAnswer":0},
{"id":445,"sentence":"有(一)些人喜欢上夜班。","pinyin":"Yǒu (yì) xiē rén xǐ huan shàng yè bān.","english":"Some people like to work at night.","options":["Some people like to work at night","Some people like to work in the morning","Some people like to rest at night","Some people like to sleep at night"],"correctAnswer":0},
{"id":446,"sentence":"你觉得这个视频有用吗？","pinyin":"Nǐ jué de zhè gè shì pín yǒu yòng ma?","english":"Did you find this video useful?","options":["Did you find this video useful?","Did you find this video boring?","Did you watch this video?","Did you like this video?"],"correctAnswer":0},
{"id":447,"sentence":"我的右手受伤了。","pinyin":"Wǒ de yòu shǒu shòu shāng le.","english":"My right hand is injured.","options":["My right hand is injured","My left hand is injured","My leg is injured","My head is injured"],"correctAnswer":0},
{"id":448,"sentence":"酒店在车站的右边。","pinyin":"Jiǔ diàn zài chē zhàn de yòu bian.","english":"The hotel is on the right side of the station.","options":["The hotel is on the right side of the station","The hotel is on the left side of the station","The hotel is in front of the station","The hotel is behind the station"],"correctAnswer":0},
{"id":449,"sentence":"我喜欢在雨中散步。","pinyin":"Wǒ xǐ huan zài yǔ zhōng sàn bù.","english":"I like to walk in the rain.","options":["I like to walk in the rain","I like to walk in the sun","I like to walk at night","I like to walk in the park"],"correctAnswer":0},
{"id":450,"sentence":"这条裤子五百元。","pinyin":"Zhè tiáo kù zi wǔ bǎi yuán.","english":"The pair of pants costs five hundred yuan.","options":["The pair of pants costs five hundred yuan","The pair of pants costs fifty yuan","The pair of pants costs five thousand yuan","The pair of pants costs one hundred yuan"],"correctAnswer":0},

{"id":451,"sentence":"你家离地铁站远吗？","pinyin":"Nǐ jiā lí dì tiě zhàn yuǎn ma?","english":"Is your home far from the metro station?","options":["Is your home far from the metro station?","Is your home near the metro station?","Is your office far from the metro station?","Is your school far from the metro station?"],"correctAnswer":0},
{"id":452,"sentence":"他学中文六个月了。","pinyin":"Tā xué zhōng wén liù gè yuè le.","english":"He has been learning Chinese for 6 months.","options":["He has been learning Chinese for 6 months","He has been learning Chinese for 6 years","He has been learning Chinese for 3 months","He has been learning Chinese for 1 year"],"correctAnswer":0},
{"id":453,"sentence":"再做一次。","pinyin":"Zài zuò yí cì.","english":"Do it again.","options":["Do it again","Do it later","Stop doing it","Do it now"],"correctAnswer":0},
{"id":454,"sentence":"再见！","pinyin":"Zài jiàn!","english":"Goodbye!","options":["Goodbye!","Hello!","See you later!","Good night!"],"correctAnswer":0},
{"id":455,"sentence":"你在办公室吗？","pinyin":"Nǐ zài bàn gōng shì ma?","english":"Are you in the office?","options":["Are you in the office?","Are you at home?","Are you at school?","Are you outside?"],"correctAnswer":0},
{"id":456,"sentence":"你在家吗？","pinyin":"Nǐ zài jiā ma?","english":"Are you at home?","options":["Are you at home?","Are you at school?","Are you at work?","Are you outside?"],"correctAnswer":0},
{"id":457,"sentence":"我要早睡早起。","pinyin":"Wǒ yào zǎo shuì zǎo qǐ.","english":"I want to go to bed early and get up early.","options":["I want to go to bed early and get up early","I want to stay up late and sleep late","I want to sleep during the day","I want to sleep in the afternoon"],"correctAnswer":0},
{"id":458,"sentence":"你早饭吃了什么？","pinyin":"Nǐ zǎo fàn chī le shén me?","english":"What did you eat for breakfast?","options":["What did you eat for breakfast?","What did you eat for lunch?","What did you eat for dinner?","Did you eat breakfast?"],"correctAnswer":0},
{"id":459,"sentence":"早上好！","pinyin":"Zǎo shang hǎo!","english":"Good morning!","options":["Good morning!","Good afternoon!","Good evening!","Good night!"],"correctAnswer":0},
{"id":460,"sentence":"你知道怎么做饺子吗？","pinyin":"Nǐ zhī dào zěn me zuò jiǎo zi ma?","english":"Do you know how to make dumplings?","options":["Do you know how to make dumplings?","Do you know how to make noodles?","Do you know how to make rice?","Do you know how to cook soup?"],"correctAnswer":0},
{"id":461,"sentence":"我在火车站等你。","pinyin":"Wǒ zài huǒ chē zhàn děng nǐ.","english":"I'm waiting for you at the train station.","options":["I'm waiting for you at the train station","I'm waiting for you at the airport","I'm waiting for you at school","I'm waiting for you at home"],"correctAnswer":0},
{"id":462,"sentence":"我在找我的手机。","pinyin":"Wǒ zài zhǎo wǒ de shǒu jī.","english":"I'm looking for my phone.","options":["I'm looking for my phone","I'm looking for my keys","I'm looking for my wallet","I'm looking for my bag"],"correctAnswer":0},
{"id":463,"sentence":"你找到工作了吗？","pinyin":"Nǐ zhǎo dào gōng zuò le ma?","english":"Have you found a job?","options":["Have you found a job?","Have you found a friend?","Have you found your book?","Have you found your phone?"],"correctAnswer":0},
{"id":464,"sentence":"这是我的手机。","pinyin":"Zhè shì wǒ de shǒu jī.","english":"This is my cell phone.","options":["This is my cell phone","This is my tablet","This is my laptop","This is my wallet"],"correctAnswer":0},
{"id":465,"sentence":"你的教室在这边。","pinyin":"Nǐ de jiào shì zài zhè biān.","english":"Your classroom is here.","options":["Your classroom is here","Your office is here","Your home is here","Your school is here"],"correctAnswer":0},
{"id":466,"sentence":"这里的菜很好吃。","pinyin":"Zhè lǐ de cài hěn hǎo chī.","english":"The food here is delicious.","options":["The food here is delicious","The food here is spicy","The food here is cold","The food here is expensive"],"correctAnswer":0},
{"id":467,"sentence":"我常常在这儿健身。","pinyin":"Wǒ cháng cháng zài zhèr jiàn shēn.","english":"I often work out here.","options":["I often work out here","I often read here","I often eat here","I often sleep here"],"correctAnswer":0},
{"id":468,"sentence":"这些甜点都是你做的吗？","pinyin":"Zhè xiē tián diǎn dōu shì nǐ zuò de ma?","english":"Did you make all these desserts?","options":["Did you make all these desserts?","Did you buy all these desserts?","Did someone else make the desserts?","Did you eat all these desserts?"],"correctAnswer":0},
{"id":469,"sentence":"他站着。","pinyin":"Tā zhàn zhe.","english":"He is standing.","options":["He is standing","He is sitting","He is lying down","He is running"],"correctAnswer":0},
{"id":470,"sentence":"你真聪明。","pinyin":"Nǐ zhēn cōng ming.","english":"You are really smart.","options":["You are really smart","You are really tall","You are really strong","You are really kind"],"correctAnswer":0},
{"id":471,"sentence":"这新闻是真的吗？","pinyin":"Zhè xīn wén shì zhēn de ma?","english":"Is this news true?","options":["Is this news true?","Is this news fake?","Is this news interesting?","Is this news old?"],"correctAnswer":0},
{"id":472,"sentence":"我正开车呢。","pinyin":"Wǒ zhèng kāi chē ne.","english":"I am driving.","options":["I am driving","I am walking","I am running","I am eating"],"correctAnswer":0},
{"id":473,"sentence":"我正在健身。","pinyin":"Wǒ zhèng zài jiàn shēn.","english":"I'm working out.","options":["I'm working out","I'm resting","I'm sleeping","I'm studying"],"correctAnswer":0},
{"id":474,"sentence":"我不知道。","pinyin":"Wǒ bù zhī dào.","english":"I don't know.","options":["I don't know","I know","I forgot","I understand"],"correctAnswer":0},
{"id":475,"sentence":"他的历史知识很浅薄。","pinyin":"Tā de lì shǐ zhī shi hěn qiǎn bó.","english":"His historical knowledge is shallow.","options":["His historical knowledge is shallow","His historical knowledge is deep","His historical knowledge is excellent","His historical knowledge is average"],"correctAnswer":0},
{"id":476,"sentence":"她在电影中演一个妈妈。","pinyin":"Tā zài diàn yǐng zhōng yǎn yí gè mā ma.","english":"She plays a mom in the movie.","options":["She plays a mom in the movie","She plays a teacher in the movie","She plays a student in the movie","She plays a doctor in the movie"],"correctAnswer":0},
{"id":477,"sentence":"你去过中国吗？","pinyin":"Nǐ qù guò zhōng guó ma?","english":"Have you been to China?","options":["Have you been to China?","Have you been to Japan?","Have you been to America?","Have you been to Europe?"],"correctAnswer":0},
{"id":478,"sentence":"我的车停在中间。","pinyin":"Wǒ de chē tíng zài zhōng jiān.","english":"My car is parked in the middle.","options":["My car is parked in the middle","My car is parked on the side","My car is parked at the front","My car is parked behind"],"correctAnswer":0},
{"id":479,"sentence":"你的中文怎么样？","pinyin":"Nǐ de zhōng wén zěn me yàng?","english":"How is your Chinese?","options":["How is your Chinese?","How is your English?","How is your math?","How is your reading?"],"correctAnswer":0},
{"id":480,"sentence":"我们中午一起吃午饭吧！","pinyin":"Wǒ men zhōng wǔ yī qǐ chī wǔ fàn ba!","english":"Let's have lunch together at noon!","options":["Let's have lunch together at noon","Let's have breakfast together","Let's have dinner together","Let's have a snack together"],"correctAnswer":0},
{"id":481,"sentence":"他是中学老师。","pinyin":"Tā shì zhōng xué lǎo shī.","english":"He is a middle school teacher.","options":["He is a middle school teacher","He is a college teacher","He is an elementary school teacher","He is a university professor"],"correctAnswer":0},
{"id":482,"sentence":"那个中学生很高。","pinyin":"Nà gè zhōng xué shēng hěn gāo.","english":"That middle school student is tall.","options":["That middle school student is tall","That middle school student is short","That middle school student is smart","That middle school student is young"],"correctAnswer":0},
{"id":483,"sentence":"我的行李很重。","pinyin":"Wǒ de xíng lǐ hěn zhòng.","english":"My luggage is heavy.","options":["My luggage is heavy","My luggage is light","My luggage is big","My luggage is small"],"correctAnswer":0},
{"id":484,"sentence":"汉语声调很重要。","pinyin":"Hàn yǔ shēng diào hěn zhòng yào.","english":"Chinese tones are very important.","options":["Chinese tones are very important","Chinese grammar is very important","Chinese vocabulary is very important","Chinese writing is very important"],"correctAnswer":0},
{"id":485,"sentence":"你住在哪里？","pinyin":"Nǐ zhù zài nǎ lǐ?","english":"Where do you live?","options":["Where do you live?","Where do you work?","Where do you study?","Where do you go shopping?"],"correctAnswer":0},
{"id":486,"sentence":"我要准备晚饭。","pinyin":"Wǒ yào zhǔn bèi wǎn fàn.","english":"I'm going to prepare dinner.","options":["I'm going to prepare dinner","I'm going to prepare breakfast","I'm going to prepare lunch","I'm going to prepare dessert"],"correctAnswer":0},
{"id":487,"sentence":"这张桌子多长？","pinyin":"Zhè zhāng zhuō zi duō cháng?","english":"How long is this table?","options":["How long is this table?","How wide is this table?","How heavy is this table?","How tall is this table?"],"correctAnswer":0},
{"id":488,"sentence":"这是什么字？","pinyin":"Zhè shì shén me zì?","english":"What character is this?","options":["What character is this?","What word is this?","What sentence is this?","What number is this?"],"correctAnswer":0},
{"id":489,"sentence":"请给我一把刀子和叉子。","pinyin":"Qǐng gěi wǒ yī bǎ dāo zi hé chā zi.","english":"Please give me a knife and fork.","options":["Please give me a knife and fork","Please give me a spoon and plate","Please give me chopsticks and bowl","Please give me a cup and spoon"],"correctAnswer":0},
{"id":490,"sentence":"走吧！","pinyin":"Zǒu ba!","english":"Let's go!","options":["Let's go!","Stop!","Wait!","Come here!"],"correctAnswer":0},
{"id":491,"sentence":"他常常走路去学校。","pinyin":"Tā cháng cháng zǒu lù qù xué xiào.","english":"He often walks to school.","options":["He often walks to school","He often drives to school","He often bikes to school","He often takes the bus to school"],"correctAnswer":0},
{"id":492,"sentence":"你最喜欢哪个季节？","pinyin":"Nǐ zuì xǐ huan nǎ gè jì jié?","english":"Which season do you like the most?","options":["Which season do you like the most?","Which month do you like the most?","Which day do you like the most?","Which holiday do you like the most?"],"correctAnswer":0},
{"id":493,"sentence":"你最好的朋友是谁？","pinyin":"Nǐ zuì hǎo de péng you shì shéi?","english":"Who is your best friend?","options":["Who is your best friend?","Who is your teacher?","Who is your classmate?","Who is your neighbor?"],"correctAnswer":0},
{"id":494,"sentence":"今天是最后一天。","pinyin":"Jīn tiān shì zuì hòu yī tiān.","english":"Today is the last day.","options":["Today is the last day","Today is the first day","Today is a holiday","Today is Monday"],"correctAnswer":0},
{"id":495,"sentence":"你昨天加班了吗？","pinyin":"Nǐ zuó tiān jiā bān le ma?","english":"Did you work overtime yesterday?","options":["Did you work overtime yesterday?","Did you work yesterday?","Did you rest yesterday?","Did you study yesterday?"],"correctAnswer":0},
{"id":496,"sentence":"你用左手写字吗？","pinyin":"Nǐ yòng zuǒ shǒu xiě zì ma?","english":"Do you write with your left hand?","options":["Do you write with your left hand?","Do you write with your right hand?","Do you type with your left hand?","Do you type with your right hand?"],"correctAnswer":0},
{"id":497,"sentence":"停车场在超市的左边。","pinyin":"Tíng chē chǎng zài chāo shì de zuǒ bian.","english":"The parking lot is on the left side of the supermarket.","options":["The parking lot is on the left side of the supermarket","The parking lot is on the right side of the supermarket","The parking lot is behind the supermarket","The parking lot is in front of the supermarket"],"correctAnswer":0},
{"id":498,"sentence":"我可以坐在这里吗？","pinyin":"Wǒ kě yǐ zuò zài zhè lǐ ma?","english":"Can I sit here?","options":["Can I sit here?","Can I stand here?","Can I lie here?","Can I wait here?"],"correctAnswer":0},
{"id":499,"sentence":"我们坐下喝杯茶吧。","pinyin":"Wǒ men zuò xià hē bēi chá ba.","english":"Let's sit down and have a cup of tea.","options":["Let's sit down and have a cup of tea","Let's stand and have a cup of tea","Let's walk and have a cup of tea","Let's lie down and have a cup of tea"],"correctAnswer":0},
{"id":500,"sentence":"你下班后要做什么？","pinyin":"Nǐ xià bān hòu yào zuò shén me?","english":"What are you going to do after work?","options":["What are you going to do after work?","What did you do after work?","What are you doing at work?","What will you do tomorrow?"],"correctAnswer":0}


]

@sentence_bp.route('/quiz')
def sentence_quiz():
    """Render the sentence quiz page"""
    return render_template('quiz_sentences.html')

@sentence_bp.route('/api/quiz-sentences')
def get_quiz_sentences():
    """API endpoint to get sentences for the quiz"""
    try:
        # Get number of questions from request (default 20)
        num_questions = int(request.args.get('count', 20))
        
        # Select random sentences for the quiz
        quiz_sentences = random.sample(HSK1_SENTENCES, min(num_questions, len(HSK1_SENTENCES)))
        
        # Create a deep copy and randomize the position of correct answers
        randomized_sentences = []
        for sentence in quiz_sentences:
            # Create a copy to avoid modifying the original data
            sentence_copy = sentence.copy()
            sentence_copy['options'] = sentence['options'].copy()
            
            # Store the correct English translation before shuffling
            correct_english = sentence['english']
            
            # Randomize options
            random.shuffle(sentence_copy['options'])
            
            # Find the new position of the correct answer using fuzzy matching
            try:
                sentence_copy['correctAnswer'] = sentence_copy['options'].index(correct_english)
            except ValueError:
                # If exact match fails, try case-insensitive matching
                found_index = None
                for i, option in enumerate(sentence_copy['options']):
                    if option.lower().strip() == correct_english.lower().strip():
                        found_index = i
                        break
                
                if found_index is not None:
                    sentence_copy['correctAnswer'] = found_index
                else:
                    # If still not found, use the original correctAnswer position
                    # but make sure it's within bounds after shuffling
                    original_index = min(sentence['correctAnswer'], len(sentence_copy['options']) - 1)
                    sentence_copy['correctAnswer'] = original_index
            
            randomized_sentences.append(sentence_copy)
        
        return jsonify({
            'success': True,
            'sentences': randomized_sentences,
            'total_sentences': len(HSK1_SENTENCES),
            'quiz_count': num_questions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving quiz sentences: {str(e)}'
        }), 500

@sentence_bp.route('/api/all-sentences')
def get_all_sentences():
    """API endpoint to get all HSK1 sentences"""
    try:
        return jsonify({
            'success': True,
            'sentences': HSK1_SENTENCES
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sentences: {str(e)}'
        }), 500

@sentence_bp.route('/api/next-quiz')
def get_next_quiz():
    """API endpoint to get a new quiz with different sentences"""
    try:
        # Get previously used sentence IDs from session
        used_ids = session.get('used_sentence_ids', [])
        
        # Get available sentences (not used before)
        available_sentences = [sentence for sentence in HSK1_SENTENCES if sentence['id'] not in used_ids]
        
        # If we don't have enough new sentences, reset and use all sentences
        num_questions = int(request.args.get('count', 20))
        if len(available_sentences) < num_questions:
            available_sentences = HSK1_SENTENCES.copy()
            used_ids = []
        
        # Select new sentences
        quiz_sentences = random.sample(available_sentences, min(num_questions, len(available_sentences)))
        
        # Update used sentence IDs in session
        new_used_ids = used_ids + [sentence['id'] for sentence in quiz_sentences]
        session['used_sentence_ids'] = new_used_ids
        
        # Create randomized versions
        randomized_sentences = []
        for sentence in quiz_sentences:
            sentence_copy = sentence.copy()
            sentence_copy['options'] = sentence['options'].copy()
            
            correct_english = sentence['english']
            random.shuffle(sentence_copy['options'])
            
            # Find the new position of the correct answer using fuzzy matching
            try:
                sentence_copy['correctAnswer'] = sentence_copy['options'].index(correct_english)
            except ValueError:
                # If exact match fails, try case-insensitive matching
                found_index = None
                for i, option in enumerate(sentence_copy['options']):
                    if option.lower().strip() == correct_english.lower().strip():
                        found_index = i
                        break
                
                if found_index is not None:
                    sentence_copy['correctAnswer'] = found_index
                else:
                    # If still not found, use the original correctAnswer position
                    # but make sure it's within bounds after shuffling
                    original_index = min(sentence['correctAnswer'], len(sentence_copy['options']) - 1)
                    sentence_copy['correctAnswer'] = original_index
            
            randomized_sentences.append(sentence_copy)
        
        return jsonify({
            'success': True,
            'sentences': randomized_sentences,
            'total_sentences': len(HSK1_SENTENCES),
            'new_sentences_count': len(quiz_sentences)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving next quiz: {str(e)}'
        }), 500

@sentence_bp.route('/api/sentence/<int:sentence_id>')
def get_sentence_detail(sentence_id):
    """API endpoint to get detailed information about a specific sentence"""
    try:
        sentence = next((s for s in HSK1_SENTENCES if s['id'] == sentence_id), None)
        
        if sentence:
            return jsonify({
                'success': True,
                'sentence': sentence
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Sentence not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sentence: {str(e)}'
        }), 500

@sentence_bp.route('/api/sentence-search')
def search_sentences():
    """API endpoint to search sentences by English or Chinese"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({
                'success': True,
                'sentences': []
            })
        
        # Search in both English and Chinese
        results = [
            sentence for sentence in HSK1_SENTENCES 
            if query in sentence['english'].lower() or query in sentence['sentence'].lower()
        ]
        
        return jsonify({
            'success': True,
            'sentences': results[:20]  # Limit to 20 results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching sentences: {str(e)}'
        }), 500
        
        


@sentence_bp.route('/api/speech-sentences')
def get_speech_sentences():
    """API endpoint specifically for speech practice - returns all sentences"""
    try:
        # Return all sentences for speech practice
        return jsonify({
            'success': True,
            'sentences': HSK1_SENTENCES,
            'total_count': len(HSK1_SENTENCES)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sentences: {str(e)}'
        }), 500        

@sentence_bp.route('/api/sentence-stats')
def get_sentence_stats():
    """API endpoint to get sentence statistics"""
    try:
        total_sentences = len(HSK1_SENTENCES)
        
        # Count sentences by type (question, statement, etc.)
        sentence_types = {}
        for sentence in HSK1_SENTENCES:
            # Simple classification based on punctuation
            if '?' in sentence['sentence']:
                sentence_type = 'question'
            elif '!' in sentence['sentence']:
                sentence_type = 'exclamation'
            else:
                sentence_type = 'statement'
            
            if sentence_type not in sentence_types:
                sentence_types[sentence_type] = 0
            sentence_types[sentence_type] += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sentences': total_sentences,
                'sentence_types': sentence_types
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sentence stats: {str(e)}'
        }), 500