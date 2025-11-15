from flask import Blueprint, render_template, jsonify, request, session
import random

sentence_bp = Blueprint('sentence', __name__)

# HSK1 Sentences Database - Starting with 10 sentences (expand to 500)
HSK1_SENTENCES = [
    
{"id": 1, "sentence": "我爱你。", "pinyin": "Wǒ ài nǐ", "english": "I love you", "options": ["I dislike you", "I like you", "I hate you", "I love you"], "correctAnswer": 3},
{"id": 2, "sentence": "你的爱好是什么？", "pinyin": "Nǐ de ài hào shì shén me?", "english": "What is your hobby?", "options": ["What's your favorite thing?", "Where is your hobby?", "What is your hobby?", "Do you have a hobby?"], "correctAnswer": 2},
{"id": 3, "sentence": "他八岁了。", "pinyin": "Tā bā suì le.", "english": "He is eight years old", "options": ["He is eight years old", "He is five years old", "He is ten years old", "He is eighteen years old"], "correctAnswer": 0},
{"id": 4, "sentence": "我爸爸是老师。", "pinyin": "Wǒ bàba shì lǎoshī.", "english": "My father is a teacher", "options": ["My father is a teacher", "My brother is a teacher", "My teacher is my father", "My father is a doctor"], "correctAnswer": 0},
{"id": 5, "sentence": "杯子里有茶。", "pinyin": "Bēizi lǐ yǒu chá.", "english": "There is tea in the cup", "options": ["There is tea in the cup", "There is milk in the cup", "There is tea on the table", "The cup is full of water"], "correctAnswer": 0},
{"id": 6, "sentence": "他在医院工作。", "pinyin": "Tā zài yīyuàn gōngzuò.", "english": "He works in a hospital", "options": ["He works in a hospital", "He studies in a school", "He works at home", "He is in the market"], "correctAnswer": 0},
{"id": 7, "sentence": "我们坐出租车去。", "pinyin": "Wǒmen zuò chūzūchē qù.", "english": "We go by taxi", "options": ["We go by taxi", "We go on foot", "We go by bus", "We go by car"], "correctAnswer": 0},
{"id": 8, "sentence": "我不会游泳。", "pinyin": "Wǒ bú huì yóuyǒng.", "english": "I can’t swim", "options": ["I can't swim", "I don’t like swimming", "I can swim", "I’m learning to swim"], "correctAnswer": 0},
{"id": 9, "sentence": "今天的天气很好。", "pinyin": "Jīntiān de tiānqì hěn hǎo.", "english": "Today's weather is good", "options": ["Today’s weather is bad", "It’s raining today", "Today's weather is good", "It’s cold today"], "correctAnswer": 2},
{"id": 10, "sentence": "他买了一个新电脑。", "pinyin": "Tā mǎi le yī gè xīn diànnǎo.", "english": "He bought a new computer", "options": ["He bought a new computer", "He has an old computer", "He borrowed a computer", "He sold his computer"], "correctAnswer": 0},
{"id": 11, "sentence": "我喜欢吃米饭。", "pinyin": "Wǒ xǐhuān chī mǐfàn.", "english": "I like eating rice", "options": ["I like eating rice", "I don’t eat rice", "I like drinking tea", "I’m full"], "correctAnswer": 0},
{"id": 12, "sentence": "她是我的朋友。", "pinyin": "Tā shì wǒ de péngyǒu.", "english": "She is my friend", "options": ["She is my sister", "She is my friend", "She is my teacher", "She is not my friend"], "correctAnswer": 1},
{"id": 13, "sentence": "我每天都学习汉语。", "pinyin": "Wǒ měitiān dōu xuéxí hànyǔ.", "english": "I study Chinese every day", "options": ["I don’t like Chinese", "I study Chinese every day", "I study English", "I study sometimes"], "correctAnswer": 1},
{"id": 14, "sentence": "你住在哪儿？", "pinyin": "Nǐ zhù zài nǎr?", "english": "Where do you live?", "options": ["Who are you?", "Where are you going?", "Where do you live?", "What’s your name?"], "correctAnswer": 2},
{"id": 15, "sentence": "我想喝水。", "pinyin": "Wǒ xiǎng hē shuǐ.", "english": "I want to drink water", "options": ["I’m full", "I don’t like water", "I want to drink water", "I’m eating now"], "correctAnswer": 2},
{"id": 16, "sentence": "你会说汉语吗？", "pinyin": "Nǐ huì shuō hànyǔ ma?", "english": "Can you speak Chinese?", "options": ["Can you speak Chinese?", "Do you understand?", "Do you write Chinese?", "Can you read Chinese?"], "correctAnswer": 0},
{"id": 17, "sentence": "我去学校。", "pinyin": "Wǒ qù xuéxiào.", "english": "I’m going to school", "options": ["I’m at school", "I’m going home", "I’m going to school", "I’m studying"], "correctAnswer": 2},
{"id": 18, "sentence": "妈妈在厨房做饭。", "pinyin": "Māma zài chúfáng zuò fàn.", "english": "Mom is cooking in the kitchen", "options": ["Mom is sleeping", "Mom is cooking in the kitchen", "Mom is eating", "Mom is at work"], "correctAnswer": 1},
{"id": 19, "sentence": "我有一个姐姐。", "pinyin": "Wǒ yǒu yī gè jiějie.", "english": "I have an elder sister", "options": ["I have an elder sister", "I have a younger sister", "I have no sister", "I have two sisters"], "correctAnswer": 0},
{"id": 20, "sentence": "现在几点？", "pinyin": "Xiànzài jǐ diǎn?", "english": "What time is it now?", "options": ["What day is it today?", "What time is it now?", "What’s the date?", "Where are we?"], "correctAnswer": 1},
{"id": 21, "sentence": "他喜欢看书。", "pinyin": "Tā xǐhuān kàn shū.", "english": "He likes reading books", "options": ["He likes reading books", "He likes to dance", "He likes music", "He doesn’t like reading"], "correctAnswer": 0},
{"id": 22, "sentence": "明天见！", "pinyin": "Míngtiān jiàn!", "english": "See you tomorrow!", "options": ["Good morning!", "Good night!", "See you tomorrow!", "See you later!"], "correctAnswer": 2},
{"id": 23, "sentence": "请坐。", "pinyin": "Qǐng zuò.", "english": "Please sit", "options": ["Please sit", "Please stand", "Please wait", "Please eat"], "correctAnswer": 0},
{"id": 24, "sentence": "我没钱。", "pinyin": "Wǒ méi qián.", "english": "I have no money", "options": ["I have money", "I have no money", "I want money", "I lost my money"], "correctAnswer": 1},
{"id": 25, "sentence": "你叫什么名字？", "pinyin": "Nǐ jiào shénme míngzì?", "english": "What’s your name?", "options": ["What’s your name?", "Where do you live?", "How are you?", "How old are you?"], "correctAnswer": 0},
{"id": 26, "sentence": "他不在家。", "pinyin": "Tā bú zài jiā.", "english": "He is not at home", "options": ["He is at home", "He is not at home", "He is in bed", "He is eating"], "correctAnswer": 1},
{"id": 27, "sentence": "我喜欢听音乐。", "pinyin": "Wǒ xǐhuān tīng yīnyuè.", "english": "I like listening to music", "options": ["I don’t like music", "I like listening to music", "I’m learning music", "I play music"], "correctAnswer": 1},
{"id": 28, "sentence": "你忙吗？", "pinyin": "Nǐ máng ma?", "english": "Are you busy?", "options": ["Are you free?", "Are you busy?", "Where are you?", "Are you tired?"], "correctAnswer": 1},
{"id": 29, "sentence": "她会唱歌。", "pinyin": "Tā huì chàng gē.", "english": "She can sing", "options": ["She can sing", "She is dancing", "She likes music", "She is a singer"], "correctAnswer": 0},
{"id": 30, "sentence": "我在看电视。", "pinyin": "Wǒ zài kàn diànshì.", "english": "I’m watching TV", "options": ["I’m watching TV", "I’m reading a book", "I’m sleeping", "I’m studying"], "correctAnswer": 0},
{"id": 31, "sentence": "老师好！", "pinyin": "Lǎoshī hǎo!", "english": "Hello, teacher!", "options": ["Goodbye, teacher!", "Hello, teacher!", "Good morning, class!", "Hello, friend!"], "correctAnswer": 1},
{"id": 32, "sentence": "我喜欢猫。", "pinyin": "Wǒ xǐhuān māo.", "english": "I like cats", "options": ["I don’t like cats", "I like cats", "I like dogs", "I hate cats"], "correctAnswer": 1},
{"id": 33, "sentence": "他在睡觉。", "pinyin": "Tā zài shuìjiào.", "english": "He is sleeping", "options": ["He is reading", "He is sleeping", "He is working", "He is eating"], "correctAnswer": 1},
{"id": 34, "sentence": "我饿了。", "pinyin": "Wǒ è le.", "english": "I am hungry", "options": ["I am hungry", "I am full", "I am tired", "I am thirsty"], "correctAnswer": 0},
{"id": 35, "sentence": "请问，厕所在哪儿？", "pinyin": "Qǐng wèn, cèsuǒ zài nǎr?", "english": "Excuse me, where is the toilet?", "options": ["Where is the teacher?", "Excuse me, where is the toilet?", "Where are you from?", "What time is it?"], "correctAnswer": 1},
{"id": 36, "sentence": "我不会写汉字。", "pinyin": "Wǒ bú huì xiě hànzì.", "english": "I can’t write Chinese characters", "options": ["I can’t write Chinese characters", "I can read Chinese", "I can write English", "I like writing"], "correctAnswer": 0},
{"id": 37, "sentence": "他有三个哥哥。", "pinyin": "Tā yǒu sān gè gēge.", "english": "He has three elder brothers", "options": ["He has one elder brother", "He has three elder brothers", "He has two brothers", "He has no brothers"], "correctAnswer": 1},
{"id": 38, "sentence": "我在家。", "pinyin": "Wǒ zài jiā.", "english": "I am at home", "options": ["I am home", "I am not home", "I’m outside", "I’m at work"], "correctAnswer": 0},
{"id": 39, "sentence": "你要去哪里？", "pinyin": "Nǐ yào qù nǎlǐ?", "english": "Where are you going?", "options": ["What’s your name?", "Where are you going?", "Who are you?", "What time is it?"], "correctAnswer": 1},
{"id": 40, "sentence": "我累了。", "pinyin": "Wǒ lèi le.", "english": "I am tired", "options": ["I am full", "I am tired", "I am hungry", "I am sleepy"], "correctAnswer": 1},
{"id": 41, "sentence": "我喜欢喝茶。", "pinyin": "Wǒ xǐhuān hē chá.", "english": "I like drinking tea", "options": ["I like coffee", "I don’t like tea", "I like drinking tea", "I’m drinking water"], "correctAnswer": 2},
{"id": 42, "sentence": "他是中国人。", "pinyin": "Tā shì zhōngguó rén.", "english": "He is Chinese", "options": ["He is Chinese", "He is Japanese", "He is teacher", "He is student"], "correctAnswer": 0},
{"id": 43, "sentence": "我喜欢学习。", "pinyin": "Wǒ xǐhuān xuéxí.", "english": "I like studying", "options": ["I like playing", "I like studying", "I hate studying", "I don’t study"], "correctAnswer": 1},
{"id": 44, "sentence": "再见！", "pinyin": "Zàijiàn!", "english": "Goodbye!", "options": ["Hello!", "See you!", "Goodbye!", "Good night!"], "correctAnswer": 2},
{"id": 45, "sentence": "谢谢！", "pinyin": "Xièxie!", "english": "Thank you!", "options": ["Hello!", "Thank you!", "Sorry!", "Please!"], "correctAnswer": 1},
{"id": 46, "sentence": "不客气。", "pinyin": "Bú kèqì.", "english": "You’re welcome", "options": ["You’re welcome", "Thank you", "Sorry", "No problem"], "correctAnswer": 0},
{"id": 47, "sentence": "我在学习汉语。", "pinyin": "Wǒ zài xuéxí hànyǔ.", "english": "I am studying Chinese", "options": ["I am studying Chinese", "I am writing", "I am teaching", "I am cooking"], "correctAnswer": 0},
{"id": 48, "sentence": "我喜欢苹果。", "pinyin": "Wǒ xǐhuān píngguǒ.", "english": "I like apples", "options": ["I like bananas", "I like apples", "I like grapes", "I like oranges"], "correctAnswer": 1},
{"id": 49, "sentence": "他去商店。", "pinyin": "Tā qù shāngdiàn.", "english": "He goes to the store", "options": ["He goes to the store", "He is sleeping", "He goes to school", "He is cooking"], "correctAnswer": 0},
{"id": 50, "sentence": "我喜欢星期天。", "pinyin": "Wǒ xǐhuān xīngqītiān.", "english": "I like Sundays", "options": ["I like Saturdays", "I like holidays", "I like Sundays", "I like Fridays"], "correctAnswer": 2},


{"id": 51, "sentence": "他喜欢穿短裤。", "pinyin": "Tā xǐ huan chuān duǎn kù.", "english": "He likes to wear shorts", "options": ["He likes to wear shirts", "He likes to wear shorts", "He likes to wear pants", "He likes to wear shoes"], "correctAnswer": 1},
{"id": 52, "sentence": "他躺在床上。", "pinyin": "Tā tǎng zài chuáng shàng.", "english": "He is lying on the bed", "options": ["He is walking", "He is sitting on the chair", "He is lying on the bed", "He is standing"], "correctAnswer": 2},
{"id": 53, "sentence": "我每周健身四次。", "pinyin": "Wǒ měi zhōu jiàn shēn sì cì.", "english": "I work out four times a week", "options": ["I never work out", "I work out two times a week", "I work out every day", "I work out four times a week"], "correctAnswer": 3},
{"id": 54, "sentence": "从这里到车站要十分钟。", "pinyin": "Cóng zhè lǐ dào chē zhàn yào shí fēn zhōng.", "english": "It takes ten minutes from here to the station", "options": ["It takes one hour", "It takes ten minutes from here to the station", "It takes twenty minutes", "It takes five minutes"], "correctAnswer": 1},
{"id": 55, "sentence": "我错了。", "pinyin": "Wǒ cuò le.", "english": "I was wrong", "options": ["I don't know", "I was wrong", "I am right", "I forgot"], "correctAnswer": 1},
{"id": 56, "sentence": "他不打女人。", "pinyin": "Tā bù dǎ nǚ rén.", "english": "He doesn't hit women", "options": ["He hits men", "He doesn't hit women", "He hits children", "He hits women"], "correctAnswer": 1},
{"id": 57, "sentence": "我要打车去飞机场。", "pinyin": "Wǒ yào dǎ chē qù fēi jī chǎng.", "english": "I'm going to take a taxi to the airport", "options": ["I'm going to walk to the airport", "I'm going to take a bus to the airport", "I'm going to drive to the airport", "I'm going to take a taxi to the airport"], "correctAnswer": 3},
{"id": 58, "sentence": "我需要打电话给顾客。", "pinyin": "Wǒ xū yào dǎ diàn huà gěi gù kè.", "english": "I need to make a phone call to the customer", "options": ["I need to make a phone call to the customer", "I need to visit the customer", "I need to ignore the customer", "I need to write an email to the customer"], "correctAnswer": 0},
{"id": 59, "sentence": "请打开空调。", "pinyin": "Qǐng dǎ kāi kōng tiáo.", "english": "Please turn on the air conditioner", "options": ["Please close the door", "Please turn off the air conditioner", "Please turn on the air conditioner", "Please open the window"], "correctAnswer": 2},
{"id": 60, "sentence": "我喜欢和朋友打球。", "pinyin": "Wǒ xǐ huan hé péng you dǎ qiú.", "english": "I like to play ball with my friends", "options": ["I like to read books", "I like to play video games", "I like to play ball with my friends", "I like to watch movies"], "correctAnswer": 2},
{"id": 61, "sentence": "他的房子很大。", "pinyin": "Tā de fáng zi hěn dà.", "english": "His house is big", "options": ["His house is huge", "His house is big", "His house is medium", "His house is small"], "correctAnswer": 1},
{"id": 62, "sentence": "我明年要申请大学。", "pinyin": "Wǒ míng nián yào shēn qǐng dà xué.", "english": "I'm going to apply to a university next year", "options": ["I already applied to university", "I'm going to apply to a university next year", "I am taking a gap year", "I will never go to university"], "correctAnswer": 1},
{"id": 63, "sentence": "现在的大学生压力很大。", "pinyin": "Xiàn zài de dà xué shēng yā lì hěn dà.", "english": "University students of today are under a lot of pressure", "options": ["They have no pressure", "They are carefree", "University students of today are under a lot of pressure", "They are relaxed"], "correctAnswer": 2},
{"id": 64, "sentence": "我五分钟后到。", "pinyin": "Wǒ wǔ fēn zhōng hòu dào.", "english": "I will arrive in five minutes", "options": ["I will not arrive", "I will arrive in one hour", "I will arrive tomorrow", "I will arrive in five minutes"], "correctAnswer": 3},
{"id": 65, "sentence": "他想得到奖学金。", "pinyin": "Tā xiǎng dé dào jiǎng xué jīn.", "english": "He wants to get the scholarship", "options": ["He wants to get a car", "He wants to get a job", "He wants to get the scholarship", "He wants to get a medal"], "correctAnswer": 2},
{"id": 66, "sentence": "她伤心地哭了。", "pinyin": "Tā shāng xīn de kū le.", "english": "She cried sadly", "options": ["She smiled", "She cried sadly", "She shouted angrily", "She laughed happily"], "correctAnswer": 1},
{"id": 67, "sentence": "这是奥利的手机。", "pinyin": "Zhè shì Ào lì de shǒu jī.", "english": "This is Ollie's phone", "options": ["This is your phone", "This is Jack's phone", "This is my phone", "This is Ollie's phone"], "correctAnswer": 3},
{"id": 68, "sentence": "我会等你的。", "pinyin": "Wǒ huì děng nǐ de.", "english": "I will wait for you", "options": ["I will call you", "I will wait for you", "I will leave now", "I will ignore you"], "correctAnswer": 1},
{"id": 69, "sentence": "钥匙在地上。", "pinyin": "Yào shi zài dì shang.", "english": "The key is on the ground", "options": ["The key is in the drawer", "The key is on the ground", "The key is on the table", "The key is in the bag"], "correctAnswer": 1},
{"id": 70, "sentence": "会议地点在哪里？", "pinyin": "Huì yì dì diǎn zài nǎ lǐ?", "english": "Where's the meeting location?", "options": ["Where's the park?", "Where's the restaurant?", "Where's the meeting location?", "Where's the hotel?"], "correctAnswer": 2},
{"id": 71, "sentence": "这个地方真漂亮。", "pinyin": "Zhè gè dì fang zhēn piào liang.", "english": "This place is so beautiful", "options": ["This place is boring", "This place is ugly", "This place is big", "This place is so beautiful"], "correctAnswer": 3},
{"id": 72, "sentence": "地上有很多水。", "pinyin": "Dì shang yǒu hěn duō shuǐ.", "english": "There is a lot of water on the ground", "options": ["There is no water", "There is sand", "There is a lot of water on the ground", "There is mud"], "correctAnswer": 2},
{"id": 73, "sentence": "这是中国地图。", "pinyin": "Zhè shì Zhōng guó dì tú.", "english": "This is a map of China", "options": ["This is a map of Europe", "This is a map of China", "This is a map of Africa", "This is a map of Japan"], "correctAnswer": 1},
{"id": 74, "sentence": "我有一个弟弟。", "pinyin": "Wǒ yǒu yí gè dì di.", "english": "I have a younger brother", "options": ["I have an older brother", "I have a younger brother", "I have a sister", "I have no siblings"], "correctAnswer": 1},
{"id": 75, "sentence": "这是我第五次来中国。", "pinyin": "Zhè shì wǒ dì wǔ cì lái Zhōng guó.", "english": "This is my fifth visit to China", "options": ["This is my fifth visit to China", "This is my first visit to China", "This is my third visit", "This is my tenth visit"], "correctAnswer": 0},
{"id": 76, "sentence": "现在三点了。", "pinyin": "Xiàn zài sān diǎn le.", "english": "It's three o'clock now", "options": ["It's five o'clock", "It's four o'clock", "It's three o'clock now", "It's two o'clock"], "correctAnswer": 2},
{"id": 77, "sentence": "没有电。", "pinyin": "Méi yǒu diàn.", "english": "No electricity", "options": ["No electricity", "The battery is full", "The lights are on", "There is electricity"], "correctAnswer": 0},
{"id": 78, "sentence": "你的电话号码是多少？", "pinyin": "Nǐ de diàn huà hào mǎ shì duō shao?", "english": "What is your phone number?", "options": ["What is your bank account?", "What is your house number?", "What is your phone number?", "What is your ID number?"], "correctAnswer": 2},
{"id": 79, "sentence": "我要买一台电脑。", "pinyin": "Wǒ yào mǎi yī tái diàn nǎo.", "english": "I want to buy a computer", "options": ["I want to buy a TV", "I want to buy a printer", "I want to buy a phone", "I want to buy a computer"], "correctAnswer": 3},
{"id": 80, "sentence": "他每天看电视。", "pinyin": "Tā měi tiān kàn diàn shì.", "english": "He watches TV every day", "options": ["He watches movies every day", "He watches TV every day", "He listens to music every day", "He reads books every day"], "correctAnswer": 1},
{"id": 81, "sentence": "我的电视机坏了。", "pinyin": "Wǒ de diàn shì jī huài le.", "english": "My TV is broken", "options": ["My TV is working", "My TV is new", "My TV is off", "My TV is broken"], "correctAnswer": 3},
{"id": 82, "sentence": "我昨天看了一部电影。", "pinyin": "Wǒ zuó tiān kàn le yí bù diàn yǐng.", "english": "I watched a movie yesterday", "options": ["I watched a play yesterday", "I watched nothing yesterday", "I watched a movie yesterday", "I watched a TV show yesterday"], "correctAnswer": 2},
{"id": 83, "sentence": "电影院在哪里？", "pinyin": "Diàn yǐng yuàn zài nǎ lǐ?", "english": "Where is the cinema?", "options": ["Where is the theater?", "Where is the cinema?", "Where is the school?", "Where is the park?"], "correctAnswer": 1},
{"id": 84, "sentence": "房子朝东。", "pinyin": "Fáng zi cháo dōng.", "english": "The house faces east", "options": ["The house faces west", "The house faces east", "The house faces south", "The house faces north"], "correctAnswer": 1},
{"id": 85, "sentence": "车库在房子的东边。", "pinyin": "Chē kù zài fáng zi de dōng biān.", "english": "The garage is on the east side of the house", "options": ["The garage is on the south side", "The garage is on the east side of the house", "The garage is on the north side", "The garage is on the west side"], "correctAnswer": 1},
{"id": 86, "sentence": "他买了很多东西。", "pinyin": "Tā mǎi le hěn duō dōng xi.", "english": "He bought a lot of things", "options": ["He bought nothing", "He bought a lot of things", "He sold a lot of things", "He bought a few things"], "correctAnswer": 1},
{"id": 87, "sentence": "别动。", "pinyin": "Bié dòng.", "english": "Don't move", "options": ["Move", "Don't move", "Sit down", "Run"], "correctAnswer": 1},
{"id": 88, "sentence": "他喜欢看动作片。", "pinyin": "Tā xǐ huan kàn dòng zuò piàn.", "english": "He likes to watch action movies", "options": ["He likes to watch action movies", "He likes to watch dramas", "He likes to watch documentaries", "He likes to watch comedies"], "correctAnswer": 0},
{"id": 89, "sentence": "我们都是朋友。", "pinyin": "Wǒ men dōu shì péng you.", "english": "We are all friends", "options": ["We are all strangers", "We are friends", "We are enemies", "We are colleagues"], "correctAnswer": 1},
{"id": 90, "sentence": "请读这句话。", "pinyin": "Qǐng dú zhè jù huà.", "english": "Please read this sentence", "options": ["Please write this sentence", "Please read this sentence", "Please ignore this sentence", "Please memorize this sentence"], "correctAnswer": 1},
{"id": 91, "sentence": "他喜欢读书。", "pinyin": "Tā xǐ huan dú shū.", "english": "He likes reading", "options": ["He likes running", "He likes reading", "He likes singing", "He likes writing"], "correctAnswer": 1},
{"id": 92, "sentence": "你做对了。", "pinyin": "Nǐ zuò duì le.", "english": "You did it right", "options": ["You didn't do it", "You did it right", "You will do it", "You did it wrong"], "correctAnswer": 1},
{"id": 93, "sentence": "对不起。", "pinyin": "Duì bu qǐ.", "english": "Sorry", "options": ["Sorry", "You're welcome", "Excuse me", "Thank you"], "correctAnswer": 0},
{"id": 94, "sentence": "喝绿茶好处多。", "pinyin": "Hē lǜ chá hǎo chù duō.", "english": "Drinking green tea has many benefits", "options": ["Drinking green tea has no benefits", "Drinking black tea has many benefits", "Drinking water has many benefits", "Drinking green tea has many benefits"], "correctAnswer": 3},
{"id": 95, "sentence": "这个多少钱？", "pinyin": "Zhè gè duō shao qián?", "english": "How much is this?", "options": ["What is this?", "How much is this?", "Where is this?", "When is this?"], "correctAnswer": 1},
{"id": 96, "sentence": "我饿了。", "pinyin": "Wǒ è le.", "english": "I'm hungry", "options": ["I'm thirsty", "I'm sleepy", "I'm hungry", "I'm tired"], "correctAnswer": 2},
{"id": 97, "sentence": "你的儿子真可爱。", "pinyin": "Nǐ de ér zi zhēn kě ài.", "english": "Your son is so cute", "options": ["Your son is naughty", "Your son is strong", "Your son is tall", "Your son is so cute"], "correctAnswer": 3},
{"id": 98, "sentence": "利息率是百分之二。", "pinyin": "Lì xī lǜ shì bǎi fēn zhī èr.", "english": "The interest rate is two percent", "options": ["The interest rate is two percent", "The interest rate is twenty percent", "The interest rate is zero percent", "The interest rate is ten percent"], "correctAnswer": 0},
{"id": 99, "sentence": "我吃了三碗饭。", "pinyin": "Wǒ chī le sān wǎn fàn.", "english": "I ate three bowls of rice", "options": ["I ate five bowls of rice", "I ate no rice", "I ate three bowls of rice", "I ate one bowl of rice"], "correctAnswer": 2},
{"id": 100, "sentence": "这家饭店的菜很贵。", "pinyin": "Zhè jiā fàn diàn de cài hěn guì.", "english": "The food in this restaurant is expensive", "options": ["The food is cheap", "The food is free", "The food in this restaurant is expensive", "The food is normal priced"], "correctAnswer": 2},


{"id":101,"sentence":"我的房间很乱。","pinyin":"Wǒ de fáng jiān hěn luàn.","english":"My room is messy","options":["My room is clean","My room is small","My room is big","My room is messy"],"correctAnswer":3},
{"id":102,"sentence":"他的房子很好。","pinyin":"Tā de fáng zi hěn hǎo.","english":"His house is nice","options":["His house is old","His house is messy","His house is nice","His house is big"],"correctAnswer":2},
{"id":103,"sentence":"我把钱放在钱包里。","pinyin":"Wǒ bǎ qián fàng zài qián bāo lǐ.","english":"I put the money in my wallet","options":["I lost the money","I took the money out","I put the money on the table","I put the money in my wallet"],"correctAnswer":3},
{"id":104,"sentence":"你想放假吗？","pinyin":"Nǐ xiǎng fàng jià ma?","english":"Do you want to have a holiday?","options":["Do you want to sleep?","Do you want to have a holiday?","Do you want to study?","Do you want to work?"],"correctAnswer":1},
{"id":105,"sentence":"他每天四点放学。","pinyin":"Tā měi tiān sì diǎn fàng xué.","english":"He finishes school at four o'clock every day","options":["He finishes school at five o'clock","He finishes school at six o'clock","He finishes school at three o'clock","He finishes school at four o'clock every day"],"correctAnswer":3},
{"id":106,"sentence":"你会飞吗？","pinyin":"Nǐ huì fēi ma?","english":"Can you fly?","options":["Can you swim?","Can you fly?","Can you run?","Can you walk?"],"correctAnswer":1},
{"id":107,"sentence":"他想买一架飞机。","pinyin":"Tā xiǎng mǎi yī jià fēi jī.","english":"He wants to buy a plane","options":["He wants to buy a car","He wants to buy a plane","He wants to buy a boat","He wants to buy a bicycle"],"correctAnswer":1},
{"id":108,"sentence":"非常好！","pinyin":"Fēi cháng hǎo!","english":"Very good!","options":["So-so","Very good!","Not good","Okay"],"correctAnswer":1},
{"id":109,"sentence":"他数学考试得了八十分。","pinyin":"Tā shù xué kǎo shì dé le bā shí fēn.","english":"He got eighty points on his math test","options":["He got ninety points","He got eighty points on his math test","He got sixty points","He got seventy points"],"correctAnswer":1},
{"id":110,"sentence":"今天没有风。","pinyin":"Jīn tiān méi yǒu fēng.","english":"There is no wind today","options":["It is windy","There is no wind today","It is sunny","It is raining"],"correctAnswer":1},
{"id":111,"sentence":"袜子干了。","pinyin":"Wà zi gān le.","english":"The socks are dry","options":["The socks are dry","The socks are clean","The socks are wet","The socks are dirty"],"correctAnswer":0},
{"id":112,"sentence":"她的家很干净。","pinyin":"Tā de jiā hěn gān jìng.","english":"Her home is clean","options":["Her home is small","Her home is big","Her home is messy","Her home is clean"],"correctAnswer":3},
{"id":113,"sentence":"你毕业后想干什么？","pinyin":"Nǐ bì yè hòu xiǎng gàn shén me?","english":"What do you want to do after graduation?","options":["Who are you?","What do you want to do after graduation?","How are you?","Where are you going?"],"correctAnswer":1},
{"id":114,"sentence":"你在干什么？","pinyin":"Nǐ zài gàn shén me?","english":"What are you doing?","options":["Where are you?","What are you doing?","Who are you?","What did you do?"],"correctAnswer":1},
{"id":115,"sentence":"这座山很高。","pinyin":"Zhè zuò shān hěn gāo.","english":"This mountain is very high","options":["This mountain is flat","This mountain is low","This mountain is small","This mountain is very high"],"correctAnswer":3},
{"id":116,"sentence":"我很高兴。","pinyin":"Wǒ hěn gāo xìng.","english":"I'm happy","options":["I'm happy","I'm tired","I'm angry","I'm sad"],"correctAnswer":0},
{"id":117,"sentence":"别告诉她。","pinyin":"Bié gào su tā.","english":"Don't tell her","options":["Don't tell her","Tell her","Ask her","Ignore her"],"correctAnswer":0},
{"id":118,"sentence":"我哥哥是老师。","pinyin":"Wǒ gē ge shì lǎo shī.","english":"My elder brother is a teacher","options":["My elder brother is a driver","My elder brother is a student","My elder brother is a teacher","My elder brother is a doctor"],"correctAnswer":2},
{"id":119,"sentence":"你会唱这首歌吗？","pinyin":"Nǐ huì chàng zhè shǒu gē ma?","english":"Can you sing this song?","options":["Can you read?","Can you write?","Can you dance?","Can you sing this song?"],"correctAnswer":3},
{"id":120,"sentence":"我要买五个西瓜。","pinyin":"Wǒ yào mǎi wǔ gè xī guā.","english":"I want to buy five watermelons","options":["I want to buy ten bananas","I want to buy one pear","I want to buy five watermelons","I want to buy three apples"],"correctAnswer":2},
{"id":121,"sentence":"请给我一杯水。","pinyin":"Qǐng gěi wǒ yī bēi shuǐ.","english":"Please give me a glass of water","options":["Please give me a plate of food","Please give me a bottle of juice","Please give me a cup of coffee","Please give me a glass of water"],"correctAnswer":3},
{"id":122,"sentence":"我跟你一起去。","pinyin":"Wǒ gēn nǐ yī qǐ qù.","english":"I will go with you","options":["I will stay","I will go later","I will go alone","I will go with you"],"correctAnswer":3},
{"id":123,"sentence":"工人都下班了。","pinyin":"Gōng rén dōu xià bān le.","english":"The workers are all off work","options":["The workers are on leave","The workers are resting","The workers are still working","The workers are all off work"],"correctAnswer":3},
{"id":124,"sentence":"我今天的工作很多。","pinyin":"Wǒ jīn tiān de gōng zuò hěn duō.","english":"I have a lot of work today","options":["I have finished all work","I have a lot of work today","I have no work today","I have little work today"],"correctAnswer":1},
{"id":125,"sentence":"请关门。","pinyin":"Qǐng guān mén.","english":"Please close the door","options":["Please leave the door open","Please lock the door","Please open the door","Please close the door"],"correctAnswer":3},
{"id":126,"sentence":"记得把手机关上。","pinyin":"Jì dé bǎ shǒu jī guān shang.","english":"Remember to turn off your cell phone","options":["Remember to throw your phone away","Remember to charge your phone","Remember to turn on your cell phone","Remember to turn off your cell phone"],"correctAnswer":3},
{"id":127,"sentence":"房租太贵了。","pinyin":"Fáng zū tài guì le.","english":"The rent is too expensive","options":["The rent is free","The rent is reasonable","The rent is cheap","The rent is too expensive"],"correctAnswer":3},
{"id":128,"sentence":"你是哪国人？","pinyin":"Nǐ shì nǎ guó rén?","english":"Which country are you from?","options":["Which country are you from?","How old are you?","What is your name?","Where do you live?"],"correctAnswer":0},
{"id":129,"sentence":"中国是一个历史悠久的国家。","pinyin":"Zhōng guó shì yī gè lì shǐ yōu jiǔ de guó jiā.","english":"China is a country with a long history","options":["China is a new country","China is a small country","China is a cold country","China is a country with a long history"],"correctAnswer":3},
{"id":130,"sentence":"他在国外学习。","pinyin":"Tā zài guó wài xué xí.","english":"He is studying abroad","options":["He is studying abroad","He is studying at home","He is traveling abroad","He is working abroad"],"correctAnswer":0},
{"id":131,"sentence":"他过了口语考试。","pinyin":"Tā guò le kǒu yǔ kǎo shì.","english":"He passed the speaking test","options":["He skipped the test","He got a perfect score","He failed the speaking test","He passed the speaking test"],"correctAnswer":3},
{"id":132,"sentence":"我还没做完。","pinyin":"Wǒ hái méi zuò wán.","english":"I'm not done yet","options":["I'm done","I'm not done yet","I haven't started","I will never finish"],"correctAnswer":1},
{"id":133,"sentence":"你要咖啡还是茶？","pinyin":"Nǐ yào kā fēi hái shì chá?","english":"Do you want coffee or tea?","options":["Do you want coffee or tea?","Do you want tea or milk?","Do you want wine or beer?","Do you want juice or water?"],"correctAnswer":0},
{"id":134,"sentence":"懂手语的，除了我还有三个人。","pinyin":"Dǒng shǒu yǔ de, chú le wǒ hái yǒu sān gè rén.","english":"There are three people besides me who know sign language","options":["There are ten people","There are three people besides me who know sign language","No one knows sign language","There is only me who knows sign language"],"correctAnswer":1},
{"id":135,"sentence":"她有五个孩子。","pinyin":"Tā yǒu wǔ gè hái zi.","english":"She has five children","options":["She has five children","She has no children","She has two children","She has three children"],"correctAnswer":0},
{"id":136,"sentence":"他会说汉语。","pinyin":"Tā huì shuō hàn yǔ.","english":"He can speak Mandarin Chinese","options":["He can speak Mandarin Chinese","He can speak French","He can speak Japanese","He can speak English"],"correctAnswer":0},
{"id":137,"sentence":"他今天学了十个汉字。","pinyin":"Tā jīn tiān xué le shí gè hàn zì.","english":"He learned ten Chinese characters today","options":["He learned twenty characters","He learned ten Chinese characters today","He learned five characters","He didn't learn any characters"],"correctAnswer":1},
{"id":138,"sentence":"她是一个好老师。","pinyin":"Tā shì yí gè hǎo lǎo shī.","english":"She is a good teacher","options":["She is a good teacher","She is a new teacher","She is a bad teacher","She is an average teacher"],"correctAnswer":0},
{"id":139,"sentence":"这巧克力真好吃。","pinyin":"Zhè qiǎo kè lì zhēn hǎo chī.","english":"This chocolate is so delicious","options":["This chocolate is terrible","This chocolate is so delicious","This chocolate is sweet","This chocolate is okay"],"correctAnswer":1},
{"id":140,"sentence":"这个好看吗？","pinyin":"Zhè gè hǎo kàn ma?","english":"Does this look good?","options":["Does this look good?","Does this look ugly?","Does this look bad?","Does this look okay?"],"correctAnswer":0},
{"id":141,"sentence":"这首歌好听吗？","pinyin":"Zhè shǒu gē hǎo tīng ma?","english":"Is this song good (pleasant to hear)?","options":["Is this song good (pleasant to hear)?","Is this song okay?","Is this song annoying?","Is this song bad?"],"correctAnswer":0},
{"id":142,"sentence":"这个游戏真好玩儿。","pinyin":"Zhè gè yóu xì zhēn hǎo wánr.","english":"This game is really fun","options":["This game is really fun","This game is easy","This game is difficult","This game is boring"],"correctAnswer":0},
{"id":143,"sentence":"今天几号？","pinyin":"Jīn tiān jǐ hào?","english":"What's the date today?","options":["What's the date today?","What's the month today?","What's the day today?","What's the year today?"],"correctAnswer":0},
{"id":144,"sentence":"你喝咖啡吗?","pinyin":"Nǐ hē kā fēi ma?","english":"Do you drink coffee?","options":["Do you drink water?","Do you drink coffee?","Do you drink tea?","Do you drink milk?"],"correctAnswer":1},
{"id":145,"sentence":"我喜欢黑色和白色。","pinyin":"Wǒ xǐ huan hēi sè hé bái sè.","english":"I like black and white","options":["I like pink and purple","I like red and blue","I like green and yellow","I like black and white"],"correctAnswer":3},
{"id":146,"sentence":"她的车很贵。","pinyin":"Tā de chē hěn guì.","english":"Her car is (very) expensive","options":["Her car is cheap","Her car is (very) expensive","Her car is old","Her car is medium"],"correctAnswer":1},
{"id":147,"sentence":"下班后，你来我家。","pinyin":"Xià bān hòu, nǐ lái wǒ jiā.","english":"After work, you come to my place","options":["After work, you come to my place","After lunch, you come","After school, you come","Before work, you come"],"correctAnswer":0},
{"id":148,"sentence":"车站在酒店后边。","pinyin":"Chē zhàn zài jiǔ diàn hòu biān.","english":"The station is behind the hotel","options":["The station is far away","The station is behind the hotel","The station is in front of the hotel","The station is beside the hotel"],"correctAnswer":1},
{"id":149,"sentence":"我后天去海南。","pinyin":"Wǒ hòu tiān qù hǎi nán.","english":"I'm going to Hainan the day after tomorrow","options":["I'm going to Hainan tomorrow","I'm going to Hainan the day after tomorrow","I'm going to Hainan today","I'm going to Hainan next week"],"correctAnswer":1},
{"id":150,"sentence":"你喜欢这朵花吗？","pinyin":"Nǐ xǐ huan zhè duǒ huā ma?","english":"Do you like this flower?","options":["Do you want this flower?","Do you like this flower?","Do you ignore this flower?","Do you dislike this flower?"],"correctAnswer":1},


{"id":151,"sentence":"我不明白他的话。","pinyin":"Wǒ bù míng bai tā de huà.","english":"I don't understand his words","options":["I ignore his words","I like his words","I don't understand his words","I understand his words"],"correctAnswer":2},
{"id":152,"sentence":"吸烟是个坏习惯。","pinyin":"Xī yān shì gè huài xí guàn.","english":"Smoking is a bad habit","options":["Smoking is good","Smoking is harmless","Smoking is a bad habit","Smoking is okay"],"correctAnswer":2},
{"id":153,"sentence":"你什么时候还车？","pinyin":"Nǐ shén me shí hou hái chē?","english":"When will you return the car?","options":["When will you buy the car?","When will you rent the car?","When will you sell the car?","When will you return the car?"],"correctAnswer":3},
{"id":154,"sentence":"你什么时候回中国？","pinyin":"Nǐ shén me shí hou huí zhōng guó?","english":"When will you go back to China?","options":["When will you go to Japan?","When will you go to France?","When will you go to the USA?","When will you go back to China?"],"correctAnswer":3},
{"id":155,"sentence":"请你回答。","pinyin":"Qǐng nǐ huí dá.","english":"Please answer","options":["Please ignore","Please repeat","Please answer","Please ask"],"correctAnswer":2},
{"id":156,"sentence":"他想回到上海。","pinyin":"Tā xiǎng huí dào Shàng hǎi.","english":"He wants to return to Shanghai","options":["He wants to stay here","He wants to return to Shanghai","He wants to go to Beijing","He wants to go to Guangzhou"],"correctAnswer":1},
{"id":157,"sentence":"你几点回家？","pinyin":"Nǐ jǐ diǎn huí jiā?","english":"What time do you go home?","options":["What time do you wake up?","What time do you eat?","What time do you go home?","What time do you sleep?"],"correctAnswer":2},
{"id":158,"sentence":"你什么时候回来？","pinyin":"Nǐ shén me shí hou huí lái?","english":"When will you come back?","options":["When will you leave?","When will you stay?","When will you come back?","When will you go?"],"correctAnswer":2},
{"id":159,"sentence":"你怎么回去？","pinyin":"Nǐ zěn me huí qù?","english":"How do you go back?","options":["How do you travel?","How do you go back?","How do you come here?","How do you run?"],"correctAnswer":1},
{"id":160,"sentence":"你会说中文吗？","pinyin":"Nǐ huì shuō zhōng wén ma?","english":"Can you speak Chinese?","options":["Can you speak French?","Can you speak English?","Can you speak Japanese?","Can you speak Chinese?"],"correctAnswer":3},
{"id":161,"sentence":"我坐火车去深圳。","pinyin":"Wǒ zuò huǒ chē qù Shēn zhèn.","english":"I take the train to Shenzhen","options":["I take the bus to Shenzhen","I take the train to Shenzhen","I drive to Shenzhen","I fly to Shenzhen"],"correctAnswer":1},
{"id":162,"sentence":"我在机场。","pinyin":"Wǒ zài jī chǎng.","english":"I'm at the airport","options":["I'm at the station","I'm at home","I'm at the airport","I'm at the school"],"correctAnswer":2},
{"id":163,"sentence":"你订机票了吗？","pinyin":"Nǐ dìng jī piào le ma?","english":"Have you booked an air ticket?","options":["Have you booked a train ticket?","Have you booked a taxi?","Have you booked a hotel?","Have you booked an air ticket?"],"correctAnswer":3},
{"id":164,"sentence":"你喜欢吃鸡蛋吗？","pinyin":"Nǐ xǐ huan chī jī dàn ma?","english":"Do you like to eat eggs?","options":["Do you like to eat bread?","Do you like to eat rice?","Do you like to eat noodles?","Do you like to eat eggs?"],"correctAnswer":3},
{"id":165,"sentence":"你要几杯咖啡？","pinyin":"Nǐ yào jǐ bēi kā fēi?","english":"How many cups of coffee do you want?","options":["How many cups of coffee do you want?","How many cups of juice?","How many cups of water?","How many cups of tea?"],"correctAnswer":0},
{"id":166,"sentence":"请记下这些汉字。","pinyin":"Qǐng jì xià zhè xiē hàn zì.","english":"Please note down these Chinese characters","options":["Please read these Chinese characters","Please ignore these Chinese characters","Please note down these Chinese characters","Please erase these Chinese characters"],"correctAnswer":2},
{"id":167,"sentence":"你记得我吗？","pinyin":"Nǐ jì de wǒ ma?","english":"Do you remember me?","options":["Do you forget me?","Do you ignore me?","Do you remember me?","Do you know me?"],"correctAnswer":2},
{"id":168,"sentence":"我会记住的。","pinyin":"Wǒ huì jì zhù de.","english":"I will remember","options":["I will learn","I will ignore","I will remember","I will forget"],"correctAnswer":2},
{"id":169,"sentence":"我的家在浦东。","pinyin":"Wǒ zài jiā zài Pǔ dōng.","english":"My home is in Pudong","options":["My home is in Pudong","My home is in Guangzhou","My home is in Beijing","My home is in Shanghai"],"correctAnswer":0},
{"id":170,"sentence":"我的钥匙在家里。","pinyin":"Wǒ de yào shi zài jiā lǐ.","english":"My keys are at home","options":["My keys are at home","My keys are in school","My keys are in the office","My keys are lost"],"correctAnswer":0},
{"id":171,"sentence":"今天很热。","pinyin":"Jīn tiān hěn rè.","english":"Today is very hot","options":["Today is very cold","Today is very hot","Today is windy","Today is rainy"],"correctAnswer":1},
{"id":172,"sentence":"今天是星期几？","pinyin":"Jīn tiān shì xīng qī jǐ?","english":"What day is it today?","options":["What time is it today?","What day is it today?","What month is it?","Where are we today?"],"correctAnswer":1},
{"id":173,"sentence":"你今天忙吗？","pinyin":"Nǐ jīn tiān máng ma?","english":"Are you busy today?","options":["Are you tired today?","Are you free today?","Are you hungry today?","Are you busy today?"],"correctAnswer":3},
{"id":174,"sentence":"今天下雨了。","pinyin":"Jīn tiān xià yǔ le.","english":"It rained today","options":["It rained today","It snowed today","It is sunny today","It is cloudy today"],"correctAnswer":0},
{"id":175,"sentence":"明天我不上班。","pinyin":"Míng tiān wǒ bù shàng bān.","english":"I won't go to work tomorrow","options":["I will go to work tomorrow","I won't go to work tomorrow","I will rest today","I don't work anymore"],"correctAnswer":1},
{"id":176,"sentence":"我每天六点起床。","pinyin":"Wǒ měi tiān liù diǎn qǐ chuáng.","english":"I get up at six every day","options":["I get up at six every day","I sleep at six every day","I eat at six every day","I go home at six every day"],"correctAnswer":0},
{"id":177,"sentence":"我喜欢学中文。","pinyin":"Wǒ xǐ huan xué zhōng wén.","english":"I like studying Chinese","options":["I like studying math","I hate studying Chinese","I like studying Chinese","I like studying English"],"correctAnswer":2},
{"id":178,"sentence":"你会开车吗？","pinyin":"Nǐ huì kāi chē ma?","english":"Can you drive?","options":["Can you swim?","Can you cook?","Can you drive?","Can you ride a bike?"],"correctAnswer":2},
{"id":179,"sentence":"我不会游泳。","pinyin":"Wǒ bú huì yóu yǒng.","english":"I can't swim","options":["I can't swim","I can swim","I forgot to swim","I like swimming"],"correctAnswer":0},
{"id":180,"sentence":"医院在学校旁边。","pinyin":"Yī yuàn zài xué xiào páng biān.","english":"The hospital is next to the school","options":["The hospital is behind the school","The school is next to the hospital","The hospital is next to the school","The hospital is far from the school"],"correctAnswer":2},
{"id":181,"sentence":"我在等你。","pinyin":"Wǒ zài děng nǐ.","english":"I am waiting for you","options":["I am following you","I am calling you","I am waiting for you","I am looking for you"],"correctAnswer":2},
{"id":182,"sentence":"请你帮帮我。","pinyin":"Qǐng nǐ bāng bang wǒ.","english":"Please help me","options":["Please help me","Please show me","Please ignore me","Please follow me"],"correctAnswer":0},
{"id":183,"sentence":"我忘了。","pinyin":"Wǒ wàng le.","english":"I forgot","options":["I remember","I forgot","I don't know","I understand"],"correctAnswer":1},
{"id":184,"sentence":"我想睡觉。","pinyin":"Wǒ xiǎng shuì jiào.","english":"I want to sleep","options":["I want to sleep","I want to eat","I want to run","I want to rest"],"correctAnswer":0},
{"id":185,"sentence":"你的手机响了。","pinyin":"Nǐ de shǒu jī xiǎng le.","english":"Your phone is ringing","options":["Your phone is broken","Your phone is ringing","Your phone is missing","Your phone is off"],"correctAnswer":1},
{"id":186,"sentence":"我要去上课了。","pinyin":"Wǒ yào qù shàng kè le.","english":"I’m going to class","options":["I’m going to class","I’m stopping class","I’m leaving school","I’m going home"],"correctAnswer":0},
{"id":187,"sentence":"今天没太阳。","pinyin":"Jīn tiān méi tài yáng.","english":"There is no sun today","options":["The sun is bright today","There is no sun today","It is raining today","It is windy today"],"correctAnswer":1},
{"id":188,"sentence":"我头疼。","pinyin":"Wǒ tóu téng.","english":"I have a headache","options":["I have a headache","I have a stomachache","I have a fever","I am hungry"],"correctAnswer":0},
{"id":189,"sentence":"我的电脑坏了。","pinyin":"Wǒ de diàn nǎo huài le.","english":"My computer is broken","options":["My computer is slow","My computer is broken","My computer is new","My computer is missing"],"correctAnswer":1},
{"id":190,"sentence":"我们走吧。","pinyin":"Wǒ men zǒu ba.","english":"Let's go","options":["Let's go","Let's rest","Let's wait","Let's sit"],"correctAnswer":0},
{"id":191,"sentence":"我在上班。","pinyin":"Wǒ zài shàng bān.","english":"I am at work","options":["I am at home","I am at work","I am at school","I am resting"],"correctAnswer":1},
{"id":192,"sentence":"我想喝水。","pinyin":"Wǒ xiǎng hē shuǐ.","english":"I want to drink water","options":["I want to drink juice","I want to drink coffee","I want to drink water","I want to cook food"],"correctAnswer":2},
{"id":193,"sentence":"我饿了。","pinyin":"Wǒ è le.","english":"I am hungry","options":["I am full","I am tired","I am hungry","I am sleepy"],"correctAnswer":2},
{"id":194,"sentence":"他在看电视。","pinyin":"Tā zài kàn diàn shì.","english":"He is watching TV","options":["He is watching TV","He is reading","He is eating","He is sleeping"],"correctAnswer":0},
{"id":195,"sentence":"我喜欢听音乐。","pinyin":"Wǒ xǐ huan tīng yīn yuè.","english":"I like listening to music","options":["I like listening to music","I like dancing","I like singing","I like drawing"],"correctAnswer":0},
{"id":196,"sentence":"她在唱歌。","pinyin":"Tā zài chàng gē.","english":"She is singing","options":["She is dancing","She is singing","She is reading","She is cooking"],"correctAnswer":1},
{"id":197,"sentence":"门开着。","pinyin":"Mén kāi zhe.","english":"The door is open","options":["The window is open","The door is open","The door is closed","The light is off"],"correctAnswer":1},
{"id":198,"sentence":"灯关了。","pinyin":"Dēng guān le.","english":"The light is off","options":["The light is off","The light is on","The room is dark","The switch is broken"],"correctAnswer":0},
{"id":199,"sentence":"外面很冷。","pinyin":"Wài miàn hěn lěng.","english":"It's very cold outside","options":["It's warm outside","It's windy outside","It's very cold outside","It's raining outside"],"correctAnswer":2},
{"id":200,"sentence":"我要去买东西。","pinyin":"Wǒ yào qù mǎi dōng xi.","english":"I want to go shopping","options":["I want to go home","I want to go shopping","I want to eat food","I want to sleep"],"correctAnswer":1},



{"id":201,"sentence":"你可以读课文吗？","pinyin":"Nǐ kě yǐ dú kè wén ma?","english":"Can you read the text?","options":["Can you ignore the text?","Can you read the text?","Can you understand the text?","Can you write the text?"],"correctAnswer":1},
{"id":202,"sentence":"你的口疼吗？","pinyin":"Nǐ de kǒu téng ma?","english":"Does your mouth hurt?","options":["Does your hand hurt?","Does your head hurt?","Does your leg hurt?","Does your mouth hurt?"],"correctAnswer":3},
{"id":203,"sentence":"我吃了五块蛋糕。","pinyin":"Wǒ chī le wǔ kuài dàn gāo.","english":"I ate five pieces of cake","options":["I ate four pieces of cake","I ate five pieces of cake","I ate six pieces of cake","I ate three pieces of cake"],"correctAnswer":1},
{"id":204,"sentence":"他跑得快。","pinyin":"Tā pǎo de kuài.","english":"He runs fast","options":["He walks slowly","He runs fast","He runs slowly","He walks fast"],"correctAnswer":1},
{"id":205,"sentence":"你想来我家打游戏吗？","pinyin":"Nǐ xiǎng lái wǒ jiā dǎ yóu xì ma?","english":"Do you want to come to my place to play games?","options":["Do you want to sleep at my place?","Do you want to come to my place to play games?","Do you want to eat at my place?","Do you want to study at my place?"],"correctAnswer":1},
{"id":206,"sentence":"他去年来到中国。","pinyin":"Tā qù nián lái dào Zhōng guó.","english":"He came to China last year","options":["He will go to China tomorrow","He came to China last year","He went to China next year","He is coming to China now"],"correctAnswer":1},
{"id":207,"sentence":"他们是老朋友。","pinyin":"Tā men shì lǎo péng you.","english":"They are old friends","options":["They are old friends","They are new friends","They are colleagues","They are classmates"],"correctAnswer":0},
{"id":208,"sentence":"那个老人身体很好。","pinyin":"Nà gè lǎo rén shēn tǐ hěn hǎo.","english":"The old man is in good health","options":["The old man is angry","The old man is in good health","The old man is sick","The old man is tired"],"correctAnswer":1},
{"id":209,"sentence":"你的老师怎么样？","pinyin":"Nǐ de lǎo shī zěn me yàng?","english":"How is your teacher?","options":["How is your friend?","How is your mother?","How is your father?","How is your teacher?"],"correctAnswer":3},
{"id":210,"sentence":"下雨了。","pinyin":"Xià yǔ le.","english":"It's raining now","options":["It is cloudy now","It is sunny now","It is windy now","It's raining now"],"correctAnswer":3},
{"id":211,"sentence":"你累吗？","pinyin":"Nǐ lèi ma?","english":"Are you tired?","options":["Are you hungry?","Are you happy?","Are you sick?","Are you tired?"],"correctAnswer":3},
{"id":212,"sentence":"今天很冷。","pinyin":"Jīn tiān hěn lěng.","english":"It's cold today","options":["It's hot today","It's cold today","It's warm today","It's rainy today"],"correctAnswer":1},
{"id":213,"sentence":"我的护照在包里。","pinyin":"Wǒ de hù zhào zài bāo lǐ.","english":"My passport is in the bag","options":["My passport is in the bag","My passport is on the table","My passport is at home","My passport is in the car"],"correctAnswer":0},
{"id":214,"sentence":"公园里边有一个湖。","pinyin":"Gōng yuán lǐ bian yǒu yí gè hú.","english":"There is a lake in the park","options":["There is a tree in the park","There is a lake in the park","There is a river in the park","There is a hill in the park"],"correctAnswer":1},
{"id":215,"sentence":"我有两台电脑。","pinyin":"Wǒ yǒu liǎng tái diàn nǎo.","english":"I have two computers","options":["I have one computer","I have two computers","I have four computers","I have three computers"],"correctAnswer":1},
{"id":216,"sentence":"从零开始。","pinyin":"Cóng líng kāi shǐ.","english":"Start from zero","options":["Start from five","Start from ten","Start from one","Start from zero"],"correctAnswer":3},
{"id":217,"sentence":"我要六个饺子。","pinyin":"Wǒ yào liù gè jiǎo zi.","english":"I want six dumplings","options":["I want four dumplings","I want six dumplings","I want five dumplings","I want seven dumplings"],"correctAnswer":2},
{"id":218,"sentence":"你住在几楼？","pinyin":"Nǐ zhù zài jǐ lóu?","english":"Which floor do you live on?","options":["Which city do you live in?","Which floor do you live on?","Which building do you live in?","Which room do you live in?"],"correctAnswer":1},
{"id":219,"sentence":"我在楼上。","pinyin":"Wǒ zài lóu shàng.","english":"I'm upstairs","options":["I'm in the park","I'm downstairs","I'm upstairs","I'm outside"],"correctAnswer":2},
{"id":220,"sentence":"楼下有个超市。","pinyin":"Lóu xià yǒu gè chāo shì.","english":"There is a supermarket downstairs","options":["There is a park downstairs","There is a supermarket downstairs","There is a bank downstairs","There is a restaurant downstairs"],"correctAnswer":1},
{"id":221,"sentence":"淮海路在哪里？","pinyin":"Huái hǎi lù zài nǎ lǐ?","english":"Where is Huaihai Road?","options":["Where is Nanjing Road?","Where is Shanghai Road?","Where is Huaihai Road?","Where is Beijing Road?"],"correctAnswer":2},
{"id":222,"sentence":"请在路口停车。","pinyin":"Qǐng zài lù kǒu tíng chē.","english":"Please stop at the intersection","options":["Please stop at the school","Please stop at the intersection","Please stop at the roundabout","Please stop at the traffic light"],"correctAnswer":1},
{"id":223,"sentence":"他的车在路上坏了。","pinyin":"Tā de chē zài lù shang huài le.","english":"His car broke down on the road","options":["His truck broke down on the road","His car broke down on the road","His bus broke down on the road","His bike broke down on the road"],"correctAnswer":1},
{"id":224,"sentence":"我妈妈退休了。","pinyin":"Wǒ mā ma tuì xiū le.","english":"My mom is retired","options":["My mom is traveling","My mom is retired","My dad is retired","My mom is working"],"correctAnswer":1},
{"id":225,"sentence":"小心过马路。","pinyin":"Xiǎo xīn guò mǎ lù.","english":"Be careful crossing the road","options":["Be careful crossing the river","Be careful crossing the street","Be careful crossing the park","Be careful crossing the road"],"correctAnswer":3},
{"id":226,"sentence":"我马上付款。","pinyin":"Wǒ mǎ shàng fù kuǎn.","english":"I will pay right away","options":["I will pay later","I will not pay","I will pay tomorrow","I will pay right away"],"correctAnswer":3},
{"id":227,"sentence":"你要喝水吗？","pinyin":"Nǐ yào hē shuǐ ma?","english":"Do you want water?","options":["Do you want coffee?","Do you want water?","Do you want juice?","Do you want tea?"],"correctAnswer":1},
{"id":228,"sentence":"你要买什么？","pinyin":"Nǐ yào mǎi shén me?","english":"What do you want to buy?","options":["What do you want to sell?","What do you want to buy?","What do you want to drink?","What do you want to eat?"],"correctAnswer":1},
{"id":229,"sentence":"慢一点。","pinyin":"Màn yī diǎn.","english":"Slow down","options":["Go straight","Turn left","Speed up","Slow down"],"correctAnswer":3},
{"id":230,"sentence":"你忙吗？","pinyin":"Nǐ máng ma?","english":"Are you busy?","options":["Are you tired?","Are you free?","Are you sleepy?","Are you busy?"],"correctAnswer":3},
{"id":231,"sentence":"这杯茶八块五毛。","pinyin":"Zhè bēi chá bā kuài wǔ máo.","english":"This cup of tea costs eight yuan and fifty cents","options":["This cup of tea costs five yuan","This cup of tea costs eight yuan and fifty cents","This cup of tea costs ten yuan","This cup of tea costs nine yuan"],"correctAnswer":1},
{"id":232,"sentence":"他没吸烟。","pinyin":"Tā méi xī yān.","english":"He didn't smoke","options":["He eats","He didn't smoke","He drinks","He smoked"],"correctAnswer":1},
{"id":233,"sentence":"没关系。","pinyin":"Méi guān xi.","english":"It doesn't matter","options":["Be careful","It doesn't matter","Ignore it","It matters"],"correctAnswer":1},
{"id":234,"sentence":"没什么。","pinyin":"Méi shén me.","english":"It's nothing","options":["It's something","It's nothing","It's important","It's urgent"],"correctAnswer":1},
{"id":235,"sentence":"没事儿。","pinyin":"Méi shìr.","english":"It's okay / It's all right","options":["It's bad","It's okay / It's all right","It's wrong","It's urgent"],"correctAnswer":1},
{"id":236,"sentence":"这里没有超市。","pinyin":"Zhè lǐ méi yǒu chāo shì.","english":"There is no supermarket here","options":["There is a bank here","There is no supermarket here","There is a restaurant here","There is a supermarket here"],"correctAnswer":1},
{"id":237,"sentence":"我妹妹八岁了。","pinyin":"Wǒ mèi mei bā suì le.","english":"My younger sister is eight years old","options":["My younger sister is ten years old","My younger sister is eight years old","My younger sister is nine years old","My younger sister is seven years old"],"correctAnswer":1},
{"id":238,"sentence":"你锁门了吗？","pinyin":"Nǐ suǒ mén le ma?","english":"Did you lock the door?","options":["Did you open the window?","Did you lock the door?","Did you open the door?","Did you close the window?"],"correctAnswer":1},
{"id":239,"sentence":"别在门口外面停车。","pinyin":"Bié zài mén kǒu wài miàn tíng chē.","english":"Don't park outside the doorway","options":["Don't park on the street","Don't park outside the doorway","Don't park in the park","Don't park inside"],"correctAnswer":1},
{"id":240,"sentence":"门票多少钱？","pinyin":"Mén piào duō shao qián?","english":"How much is the ticket?","options":["How much is the food?","How much is the ticket?","How much is the drink?","How much is the pen?"],"correctAnswer":1},
{"id":241,"sentence":"我喜欢和朋友们一起聊天。","pinyin":"Wǒ xǐ huan hé péng you men yī qǐ liáo tiān.","english":"I like to chat with friends","options":["I like to sleep with friends","I like to chat with friends","I like to eat with friends","I like to study with friends"],"correctAnswer":1},
{"id":242,"sentence":"他吃了三碗米饭。","pinyin":"Tā chī le sān wǎn mǐ fàn.","english":"He ate three bowls of rice","options":["He ate two bowls of rice","He ate three bowls of rice","He ate four bowls of rice","He ate one bowl of rice"],"correctAnswer":1},
{"id":243,"sentence":"你会烤面包吗？","pinyin":"Nǐ huì kǎo miàn bāo ma?","english":"Can you bake bread?","options":["Can you eat bread?","Can you bake bread?","Can you boil bread?","Can you fry bread?"],"correctAnswer":1},
{"id":244,"sentence":"你想吃面条儿吗？","pinyin":"Nǐ xiǎng chī miàn tiáor ma?","english":"Do you want some noodles?","options":["Do you want some cake?","Do you want some noodles?","Do you want some rice?","Do you want some bread?"],"correctAnswer":1},
{"id":245,"sentence":"你叫什么名字？","pinyin":"Nǐ jiào shén me míng zi?","english":"What's your name?","options":["How old are you?","What's your name?","Where do you live?","Who are you?"],"correctAnswer":1},
{"id":246,"sentence":"我不明白。","pinyin":"Wǒ bù míng bai.","english":"I don't understand","options":["I don't understand","I understand","I know","I remember"],"correctAnswer":0},
{"id":247,"sentence":"他明年结婚。","pinyin":"Tā míng nián jié hūn.","english":"He is getting married next year","options":["He is getting married next year","He got married last year","He is divorcing next year","He is traveling next year"],"correctAnswer":0},
{"id":248,"sentence":"明天见。","pinyin":"Míng tiān jiàn.","english":"See you tomorrow","options":["See you today","See you tomorrow","See you yesterday","See you later"],"correctAnswer":1},
{"id":249,"sentence":"你拿护照了吗？","pinyin":"Nǐ ná hù zhào le ma?","english":"Did you take your passport?","options":["Did you forget your passport?","Did you take your passport?","Did you find your passport?","Did you lose your passport?"],"correctAnswer":1},
{"id":250,"sentence":"你要哪个？","pinyin":"Nǐ yào nǎ gè?","english":"Which one do you want?","options":["Which one do you need?","Which one do you want?","Which one do you choose?","Which one do you like?"],"correctAnswer":1},
{"id":251,"sentence":"你在哪里？","pinyin":"Nǐ zài nǎ lǐ?","english":"Where are you?","options":["Where is it?","Where are you?","Where is he?","Where is she?"],"correctAnswer":1},
{"id":252,"sentence":"你住在哪儿？","pinyin":"Nǐ zhù zài nǎr?","english":"Where do you live?","options":["Where do you live?","Where do you work?","Where do you study?","Where do you play?"],"correctAnswer":0},
{"id":253,"sentence":"哪些是你的？","pinyin":"Nǎ xiē shì nǐ de?","english":"Which ones are yours?","options":["Which ones are mine?","Which ones are yours?","Which ones are ours?","Which ones are theirs?"],"correctAnswer":1},
{"id":254,"sentence":"那是什么？","pinyin":"Nà shì shén me?","english":"What's that?","options":["What's this?","What's that?","Who is this?","Who is that?"],"correctAnswer":1},
{"id":255,"sentence":"图书馆在那边。","pinyin":"Tú shū guǎn zài nà bian.","english":"The library is over there","options":["The library is upstairs","The library is over there","The library is here","The library is downstairs"],"correctAnswer":1},
{"id":256,"sentence":"那里的天气怎么样？","pinyin":"Nà lǐ de tiān qì zěn me yàng?","english":"What's the weather like there?","options":["Is it sunny?","What's the weather like there?","Is it raining?","What's the temperature?"],"correctAnswer":1},
{"id":257,"sentence":"那儿的甜点很好吃。","pinyin":"Nàr de tián diǎn hěn hǎo chī.","english":"The desserts there are delicious","options":["The desserts here are bad","The desserts there are delicious","The desserts here are delicious","The desserts there are bad"],"correctAnswer":1},
{"id":258,"sentence":"那些甜点我都喜欢。","pinyin":"Nà xiē tián diǎn wǒ dōu xǐ huan.","english":"I like all those desserts","options":["I like none of the desserts","I like all those desserts","I like a few desserts","I like only one dessert"],"correctAnswer":1},
{"id":259,"sentence":"你喜欢喝奶茶？","pinyin":"Nǐ xǐ huan hē nǎi chá?","english":"Do you like to drink milk tea?","options":["Do you like to drink coffee?","Do you like to drink milk tea?","Do you like to drink juice?","Do you like to drink tea?"],"correctAnswer":1},
{"id":260,"sentence":"他是由奶奶带大的。","pinyin":"Tā shì yóu nǎi nai dài dà de.","english":"He was brought up by his grandma","options":["He was brought up by his uncle","He was brought up by his grandma","He was brought up by his parents","He was brought up by his teacher"],"correctAnswer":1},



{"id":261,"sentence":"医院里男护士很少。","pinyin":"Yī yuàn lǐ nán hù shì hěn shǎo.","english":"There are very few male nurses in the hospital","options":["There are many male nurses in the hospital","There are no nurses in the hospital","There are many doctors in the hospital","There are very few male nurses in the hospital"],"correctAnswer":3},
{"id":262,"sentence":"那个男孩儿真可爱。","pinyin":"Nà gè nán háir zhēn kě ài.","english":"That boy is so cute","options":["That boy is tall","That boy is smart","That boy is so cute","That boy is funny"],"correctAnswer":2},
{"id":263,"sentence":"她有男朋友吗？","pinyin":"Tā yǒu nán péng you ma?","english":"Does she have a boyfriend?","options":["Does she have a boyfriend?","Does she have a girlfriend?","Does she have a brother?","Does she have a friend?"],"correctAnswer":0},
{"id":264,"sentence":"那个男人是谁？","pinyin":"Nà gè nán rén shì shéi?","english":"Who is that man?","options":["Who is that woman?","Who is this man?","Who is that man?","Who is this woman?"],"correctAnswer":2},
{"id":265,"sentence":"那个男生很高。","pinyin":"Nà gè nán shēng hěn gāo.","english":"That boy is tall","options":["That boy is tall","That boy is young","That boy is old","That boy is short"],"correctAnswer":0},
{"id":266,"sentence":"他的房间朝南。","pinyin":"Tā de fáng jiān cháo nán.","english":"His room faces south","options":["His room faces west","His room faces south","His room faces east","His room faces north"],"correctAnswer":1},
{"id":267,"sentence":"超市在酒店南边。","pinyin":"Chāo shì zài jiǔ diàn nán biān.","english":"The supermarket is on the south side of the hotel","options":["The supermarket is far away","The supermarket is on the south side of the hotel","The supermarket is inside the hotel","The supermarket is on the north side"],"correctAnswer":1},
{"id":268,"sentence":"你觉得汉语难吗？","pinyin":"Nǐ jué de hàn yǔ nán ma?","english":"Do you think Chinese is difficult?","options":["Do you speak Chinese?","Do you think Chinese is difficult?","Do you think Chinese is easy?","Do you like Chinese?"],"correctAnswer":1},
{"id":269,"sentence":"我要喝咖啡，你呢？","pinyin":"Wǒ yào hē kā fēi, nǐ ne?","english":"I want coffee, how about you?","options":["I want coffee, how about you?","I don't want coffee, how about you?","I want juice, how about you?","I want tea, how about you?"],"correctAnswer":0},
{"id":270,"sentence":"他能来。","pinyin":"Tā néng lái.","english":"He can come","options":["He cannot come","He will come","He can come","He won't come"],"correctAnswer":2},
{"id":271,"sentence":"你有小孩吗？","pinyin":"Nǐ yǒu xiǎo hái ma?","english":"Do you have children?","options":["Do you have friends?","Do you have children?","Do you have siblings?","Do you have pets?"],"correctAnswer":1},
{"id":272,"sentence":"你们都是学生吗？","pinyin":"Nǐ men dōu shì xué sheng ma?","english":"Are you all students?","options":["Are you all workers?","Are you all students?","Are you all friends?","Are you all teachers?"],"correctAnswer":1},
{"id":273,"sentence":"他来中国五年了。","pinyin":"Tā lái zhōng guó wǔ nián le.","english":"He has been in China for five years","options":["He will come to China next year","He left China five years ago","He has been in China for five years","He came to China yesterday"],"correctAnswer":2},
{"id":274,"sentence":"您是哪位？","pinyin":"Nín shì nǎ wèi?","english":"Who are you?","options":["Where are you?","How old are you?","What is your name?","Who are you?"],"correctAnswer":3},
{"id":275,"sentence":"冰箱里没有牛奶了。","pinyin":"Bīng xiāng lǐ méi yǒu niú nǎi le.","english":"There is no milk in the fridge","options":["There is no milk in the fridge","There is milk in the fridge","There is juice in the fridge","There is water in the fridge"],"correctAnswer":0},
{"id":276,"sentence":"我们学校有很多女老师。","pinyin":"Wǒ men xué xiào yǒu hěn duō nǚ lǎo shī.","english":"There are many female teachers in our school","options":["There are many female teachers in our school","There are many male teachers","There are few teachers","There are no female teachers"],"correctAnswer":0},
{"id":277,"sentence":"你的女儿几岁了？","pinyin":"Nǐ de nǚ'ér jǐ suì le?","english":"How old is your daughter?","options":["How old is your daughter?","How tall is your daughter?","How old is your son?","How tall is your son?"],"correctAnswer":0},
{"id":278,"sentence":"你认识那个女孩儿吗？","pinyin":"Nǐ rèn shi nà gè nǚ háir ma?","english":"Do you know that girl?","options":["Do you like that boy?","Do you know that girl?","Do you know that boy?","Do you like that girl?"],"correctAnswer":1},
{"id":279,"sentence":"你有女朋友吗？","pinyin":"Nǐ yǒu nǚ péng you ma?","english":"Do you have a girlfriend?","options":["Do you have a boyfriend?","Do you have siblings?","Do you have friends?","Do you have a girlfriend?"],"correctAnswer":3},
{"id":280,"sentence":"那个女人是谁？","pinyin":"Nà gè nǚ rén shì shéi?","english":"Who is that woman?","options":["Who is that man?","Who is this woman?","Who is this man?","Who is that woman?"],"correctAnswer":3},
{"id":281,"sentence":"那个女生很漂亮。","pinyin":"Nà gè nǚ shēng hěn piào liang.","english":"That girl is beautiful","options":["That girl is short","That girl is tall","That girl is beautiful","That girl is ugly"],"correctAnswer":2},
{"id":282,"sentence":"咖啡馆在健身房旁边。","pinyin":"Kā fēi guǎn zài jiàn shēn fáng páng biān.","english":"The cafe is next to the gym","options":["The cafe is next to the gym","The cafe is behind the gym","The cafe is far from the gym","The cafe is inside the gym"],"correctAnswer":0},
{"id":283,"sentence":"他跑得快。","pinyin":"Tā pǎo de kuài.","english":"He runs fast","options":["He walks slowly","He runs slowly","He runs fast","He walks fast"],"correctAnswer":2},
{"id":284,"sentence":"这是我的朋友。","pinyin":"Zhè shì wǒ de péng you.","english":"This is my friend","options":["This is my friend","This is my teacher","This is my brother","This is my sister"],"correctAnswer":0},
{"id":285,"sentence":"你买票了吗？","pinyin":"Nǐ mǎi piào le ma?","english":"Have you bought the ticket?","options":["Have you bought the drink?","Have you bought the food?","Have you bought the ticket?","Have you bought the book?"],"correctAnswer":2},
{"id":286,"sentence":"我要休息七天。","pinyin":"Wǒ yào xiū xi qī tiān.","english":"I'm taking seven days off","options":["I'm taking ten days off","I'm taking seven days off","I'm taking three days off","I'm taking five days off"],"correctAnswer":1},
{"id":287,"sentence":"我明天要早起。","pinyin":"Wǒ míng tiān yào zǎo qǐ.","english":"I'm going to get up early tomorrow","options":["I'm going to get up early tomorrow","I'm going to sleep late tomorrow","I'm going to get up late tomorrow","I'm going to sleep early tomorrow"],"correctAnswer":0},
{"id":288,"sentence":"你通常几点起床？","pinyin":"Nǐ tōng cháng jǐ diǎn qǐ chuáng?","english":"What time do you usually get up?","options":["What time do you usually get up?","What time do you usually go to school?","What time do you usually eat?","What time do you usually sleep?"],"correctAnswer":0},
{"id":289,"sentence":"快起来！已经十一点了。","pinyin":"Kuài qǐ lái! Yǐ jīng shí yī diǎn le.","english":"Get up quickly! It's already eleven o'clock","options":["Go back to sleep! It's eleven o'clock","Leave home! It's eleven o'clock","Eat breakfast! It's eleven o'clock","Get up quickly! It's already eleven o'clock"],"correctAnswer":3},
{"id":290,"sentence":"马路上有很多汽车。","pinyin":"Mǎ lù shàng yǒu hěn duō qì chē.","english":"There are many cars on the road","options":["There are many cars on the road","There are many people on the road","There are no cars on the road","There are many bicycles on the road"],"correctAnswer":0},
{"id":291,"sentence":"你的包裹在门前。","pinyin":"Nǐ de bāo guǒ zài mén qián.","english":"Your package is in front of the door","options":["Your package is in front of the door","Your package is behind the door","Your package is on the roof","Your package is inside the door"],"correctAnswer":0},
{"id":292,"sentence":"酒店前边有一个公园。","pinyin":"Jiǔ diàn qián biān yǒu yī gè gōng yuán.","english":"There is a park in front of the hotel","options":["There is a park behind the hotel","There is a shop in front of the hotel","There is a bank in front of the hotel","There is a park in front of the hotel"],"correctAnswer":3},
{"id":293,"sentence":"我前天给他发了邮件。","pinyin":"Wǒ qián tiān gěi tā fā le yóu jiàn.","english":"I emailed him the day before yesterday","options":["I emailed him yesterday","I emailed him last week","I emailed him the day before yesterday","I will email him tomorrow"],"correctAnswer":2},
{"id":294,"sentence":"我没有钱。","pinyin":"Wǒ méi yǒu qián.","english":"I don't have money","options":["I have a credit card","I don't have money","I have money","I have some coins"],"correctAnswer":1},
{"id":295,"sentence":"我的钱包在车里。","pinyin":"Wǒ de qián bāo zài chē lǐ.","english":"My wallet is in the car","options":["My wallet is on the desk","My wallet is at home","My wallet is in the car","My wallet is in the bag"],"correctAnswer":2},
{"id":296,"sentence":"请回答。","pinyin":"Qǐng huí dá.","english":"Please answer","options":["Please ask","Please answer","Please wait","Please leave"],"correctAnswer":1},
{"id":297,"sentence":"我明天需要请假。","pinyin":"Wǒ míng tiān xū yào qǐng jià.","english":"I need to ask for leave tomorrow","options":["I need to study tomorrow","I need to ask for leave tomorrow","I need to work tomorrow","I need to go shopping tomorrow"],"correctAnswer":1},
{"id":298,"sentence":"请进。","pinyin":"Qǐng jìn.","english":"Please come in","options":["Please come in","Please sit","Please go out","Please wait"],"correctAnswer":0},
{"id":299,"sentence":"请问地铁站在哪里？","pinyin":"Qǐng wèn dì tiě zhàn zài nǎ lǐ?","english":"Excuse me, where is the subway station?","options":["Excuse me, where is the subway station?","Excuse me, where is the bus station?","Excuse me, where is the airport?","Excuse me, where is the train station?"],"correctAnswer":0},
{"id":300,"sentence":"请坐。","pinyin":"Qǐng zuò.","english":"Please have a seat","options":["Please have a seat","Please leave","Please stand","Please wait"],"correctAnswer":0},



{"id":301,"sentence":"这是什么球？","pinyin":"Zhè shì shén me qiú?","english":"What type of ball is this?","options":["Where is the ball?","What type of ball is this?","Who has the ball?","What is your name?"],"correctAnswer":1},
{"id":302,"sentence":"他去哪里了？","pinyin":"Tā qù nǎ lǐ le?","english":"Where did he go?","options":["Where is he now?","Who is he?","Where did he go?","When did he go?"],"correctAnswer":2},
{"id":303,"sentence":"他去年结婚了。","pinyin":"Tā qù nián jié hūn le.","english":"He got married last year","options":["He got married this year","He will get married next year","He got married last year","He is not married"],"correctAnswer":2},
{"id":304,"sentence":"太热了！","pinyin":"Tài rè le!","english":"It's too hot!","options":["It's too hot!","It's perfect!","It's raining!","It's too cold!"],"correctAnswer":0},
{"id":305,"sentence":"地铁上有很多人。","pinyin":"Dì tiě shàng yǒu hěn duō rén.","english":"There are lots of people on the metro","options":["There are lots of people on the metro","The metro is closed","There is no one on the metro","The metro is empty"],"correctAnswer":0},
{"id":306,"sentence":"你认识他吗？","pinyin":"Nǐ rèn shi tā ma?","english":"Do you know him?","options":["Do you know her?","Do you know him?","Do you like her?","Do you like him?"],"correctAnswer":1},
{"id":307,"sentence":"我是认真的。","pinyin":"Wǒ shì rèn zhēn de.","english":"I'm serious","options":["I'm confused","I'm serious","I'm joking","I'm tired"],"correctAnswer":1},
{"id":308,"sentence":"今天是十月一日。","pinyin":"Jīn tiān shì shí yuè yī rì.","english":"Today is the first day of October","options":["Today is the first day of November","Today is the first day of October","Today is September first","Today is October tenth"],"correctAnswer":1},
{"id":309,"sentence":"婚礼的日期定了吗？","pinyin":"Hūn lǐ de rì qī dìng le ma?","english":"Has the wedding date been set?","options":["Is there a wedding?","Has the wedding date been set?","When is the wedding?","Who is getting married?"],"correctAnswer":1},
{"id":310,"sentence":"你喜欢吃肉吗？","pinyin":"Nǐ xǐ huan chī ròu ma?","english":"Do you like to eat meat?","options":["Do you like fruits?","Do you like to eat vegetables?","Do you like to eat meat?","Do you like to drink water?"],"correctAnswer":2},
{"id":311,"sentence":"我有三台手机。","pinyin":"Wǒ yǒu sān tái shǒu jī.","english":"I have three cell phones","options":["I have two cell phones","I have one cell phone","I have three cell phones","I have four cell phones"],"correctAnswer":2},
{"id":312,"sentence":"这座山很美。","pinyin":"Zhè zuò shān hěn měi.","english":"This mountain is beautiful","options":["This mountain is high","This mountain is beautiful","This mountain is ugly","This mountain is small"],"correctAnswer":1},
{"id":313,"sentence":"你家附近有商场吗？","pinyin":"Nǐ jiā fù jìn yǒu shāng chǎng ma?","english":"Is there a shopping mall near your home?","options":["Is there a shopping mall near your home?","Is there a hospital near your home?","Is there a park near your home?","Is there a school near your home?"],"correctAnswer":0},
{"id":314,"sentence":"你想开一家商店吗？","pinyin":"Nǐ xiǎng kāi yī jiā shāng diàn ma?","english":"Do you want to open a shop?","options":["Do you want to open a shop?","Do you want to open a hospital?","Do you want to open a restaurant?","Do you want to open a school?"],"correctAnswer":0},
{"id":315,"sentence":"桌上有一些面包。","pinyin":"Zhuō shàng yǒu yī xiē miàn bāo.","english":"There is some bread on the table","options":["There is some fruit on the table","There is some water on the table","There is some bread on the table","There is some milk on the table"],"correctAnswer":2},
{"id":316,"sentence":"你通常几点上班？","pinyin":"Nǐ tōng cháng jǐ diǎn shàng bān?","english":"What time do you usually go to work?","options":["What time do you usually go to work?","What time do you eat lunch?","What time do you go to school?","What time do you wake up?"],"correctAnswer":0},
{"id":317,"sentence":"你的书在冰箱上边。","pinyin":"Nǐ de shū zài bīng xiāng shàng bian.","english":"Your book is on top of the fridge","options":["Your book is under the fridge","Your book is on top of the fridge","Your book is next to the fridge","Your book is inside the fridge"],"correctAnswer":1},
{"id":318,"sentence":"你上车了吗？","pinyin":"Nǐ shàng chē le ma?","english":"Did you get in the car?","options":["Did you wash the car?","Did you get in the car?","Did you buy a car?","Did you get off the car?"],"correctAnswer":1},
{"id":319,"sentence":"你上次吃中国菜是什么时候？","pinyin":"Nǐ shàng cì chī zhōng guó cài shì shén me shí hou?","english":"When was the last time you had Chinese food?","options":["When was the last time you had Chinese food?","When did you go to China?","When did you cook Chinese food?","When did you learn Chinese?"],"correctAnswer":0},
{"id":320,"sentence":"你今天要上课吗？","pinyin":"Nǐ jīn tiān yào shàng kè ma?","english":"Are you going to have a class today?","options":["Are you going to have a class today?","Are you going to sleep today?","Are you going to work today?","Are you going shopping today?"],"correctAnswer":0},
{"id":321,"sentence":"你每天上网吗？","pinyin":"Nǐ měi tiān shàng wǎng ma?","english":"Do you go online every day?","options":["Do you exercise every day?","Do you go online every day?","Do you read books every day?","Do you play games every day?"],"correctAnswer":1},
{"id":322,"sentence":"你明天上午有空吗？","pinyin":"Nǐ míng tiān shàng wǔ yǒu kòng ma?","english":"Are you free tomorrow morning?","options":["Are you free tomorrow afternoon?","Are you busy tomorrow morning?","Are you free tomorrow morning?","Are you free today morning?"],"correctAnswer":2},
{"id":323,"sentence":"你在哪里上学？","pinyin":"Nǐ zài nǎ lǐ shàng xué?","english":"Where do you go to school?","options":["Where do you go to work?","Where is your home?","Where is your school?","Where do you go to school?"],"correctAnswer":3},
{"id":324,"sentence":"请少放大蒜。","pinyin":"Qǐng shǎo fàng dà suàn.","english":"Please put less garlic","options":["Please don't put garlic","Please put more garlic","Please put garlic aside","Please put less garlic"],"correctAnswer":3},
{"id":325,"sentence":"谁在敲门？","pinyin":"Shéi zài qiāo mén?","english":"Who is knocking on the door?","options":["Who is knocking on the door?","Who is in the house?","Who is outside?","Who is at the window?"],"correctAnswer":0},
{"id":326,"sentence":"他身上有一只蜘蛛。","pinyin":"Tā shēn shang yǒu yī zhī zhī zhū.","english":"There is a spider on him (on his body)","options":["There is a spider on the floor","There is a spider on him (on his body)","There is a spider outside","There is a spider on the wall"],"correctAnswer":1},
{"id":327,"sentence":"你的身体怎么样？","pinyin":"Nǐ de shēn tǐ zěn me yàng?","english":"How is your body? (How is your health?)","options":["How is your family?","How is your body? (How is your health?)","How is your mood?","How is your house?"],"correctAnswer":1},
{"id":328,"sentence":"你想吃什么？","pinyin":"Nǐ xiǎng chī shén me?","english":"What do you want to eat?","options":["What do you want to buy?","What do you want to drink?","What do you want to eat?","What do you want to do?"],"correctAnswer":2},
{"id":329,"sentence":"他没生病。","pinyin":"Tā méi shēng bìng.","english":"He didn't get sick","options":["He didn't get sick","He got sick","He is tired","He is healthy"],"correctAnswer":0},
{"id":330,"sentence":"别生气。","pinyin":"Bié shēng qì.","english":"Don't get angry","options":["Be sad","Don't get angry","Be happy","Get angry"],"correctAnswer":1},



{"id":331,"sentence":"他们经常生病。","pinyin":"Tāmen jīng cháng shēng bìng.","english":"They often get sick","options":["They are very healthy","They often get sick","They never get sick","They are tired"],"correctAnswer":1},
{"id":332,"sentence":"事情变得复杂了。","pinyin":"Shì qíng biàn de fù zá le.","english":"Things became complicated","options":["Things are simple","Things are unclear","Things became complicated","Things improved"],"correctAnswer":2},
{"id":333,"sentence":"今天很适合散步。","pinyin":"Jīn tiān hěn shì hé sàn bù.","english":"Today is perfect for a walk","options":["Today is perfect for a walk","Today is too hot to walk","Today is too cold","Today is for sleeping"],"correctAnswer":0},
{"id":334,"sentence":"我喜欢吃香蕉。","pinyin":"Wǒ xǐ huan chī xiāng jiāo.","english":"I like eating bananas","options":["I like apples","I like eating bananas","I don’t like fruit","I like grapes"],"correctAnswer":1},
{"id":335,"sentence":"你会游泳吗？","pinyin":"Nǐ huì yóu yǒng ma?","english":"Can you swim?","options":["Can you dance?","Can you run fast?","Can you swim?","Can you cook?"],"correctAnswer":2},
{"id":336,"sentence":"我们下周见。","pinyin":"Wǒ men xià zhōu jiàn.","english":"See you next week","options":["See you tomorrow","See you later","See you next month","See you next week"],"correctAnswer":3},
{"id":337,"sentence":"我忘记带钥匙了。","pinyin":"Wǒ wàng jì dài yào shi le.","english":"I forgot to bring the keys","options":["I lost my keys","I forgot to bring the keys","I brought the wrong keys","I don’t have a key"],"correctAnswer":1},
{"id":338,"sentence":"你觉得怎么样？","pinyin":"Nǐ jué de zěn me yàng?","english":"What do you think?","options":["What do you think?","Where are you going?","How old are you?","How do you feel physically?"],"correctAnswer":0},
{"id":339,"sentence":"我喜欢这里的天气。","pinyin":"Wǒ xǐ huan zhè lǐ de tiān qì.","english":"I like the weather here","options":["I like the food here","I like the weather here","I don’t like it here","I like the people here"],"correctAnswer":1},
{"id":340,"sentence":"请不要迟到。","pinyin":"Qǐng bú yào chí dào.","english":"Please don’t be late","options":["Please don’t come early","Please don’t be late","Please wait for me","Please hurry"],"correctAnswer":1},
{"id":341,"sentence":"这杯咖啡很甜。","pinyin":"Zhè bēi kā fēi hěn tián.","english":"This cup of coffee is sweet","options":["This coffee is cold","This coffee is sweet","This coffee is bitter","This coffee is hot"],"correctAnswer":1},
{"id":342,"sentence":"你准备好了吗？","pinyin":"Nǐ zhǔn bèi hǎo le ma?","english":"Are you ready?","options":["Are you tired?","Are you ready?","Are you hungry?","Are you sure?"],"correctAnswer":1},
{"id":343,"sentence":"我已经到了。","pinyin":"Wǒ yǐ jīng dào le.","english":"I’ve already arrived","options":["I’ve already arrived","I’m leaving now","I'm still far away","I'm coming soon"],"correctAnswer":0},
{"id":344,"sentence":"请再说一遍。","pinyin":"Qǐng zài shuō yí biàn.","english":"Please say it again","options":["Please speak slowly","Please repeat it","Please write it down","Please call me"],"correctAnswer":1},
{"id":345,"sentence":"她每天跑步。","pinyin":"Tā měi tiān pǎo bù.","english":"She runs every day","options":["She walks every day","She sleeps every day","She runs every day","She studies every day"],"correctAnswer":2},
{"id":346,"sentence":"我们一起走吧。","pinyin":"Wǒ men yì qǐ zǒu ba.","english":"Let’s go together","options":["Let’s stay here","Let’s go together","Let’s eat together","Let’s wait"],"correctAnswer":1},
{"id":347,"sentence":"他唱歌很好听。","pinyin":"Tā chàng gē hěn hǎo tīng.","english":"He sings very well","options":["He sings very well","He sings loudly","He sings badly","He doesn’t like singing"],"correctAnswer":0},
{"id":348,"sentence":"我在等你。","pinyin":"Wǒ zài děng nǐ.","english":"I'm waiting for you","options":["I’m following you","I’m waiting for you","I’m calling you","I’m looking for you"],"correctAnswer":1},
{"id":349,"sentence":"我们快迟到了。","pinyin":"Wǒ men kuài chí dào le.","english":"We are almost late","options":["We are early","We are almost late","We are leaving now","We have arrived"],"correctAnswer":1},
{"id":350,"sentence":"我看不见。","pinyin":"Wǒ kàn bú jiàn.","english":"I can’t see","options":["I can’t hear","I can’t see","I don’t understand","I can’t walk"],"correctAnswer":1},
{"id":351,"sentence":"你喜欢什么运动？","pinyin":"Nǐ xǐ huan shén me yùn dòng?","english":"What sport do you like?","options":["What sport do you like?","Where do you exercise?","Do you like running?","Do you play football?"],"correctAnswer":0},
{"id":352,"sentence":"我们出去吃饭吧。","pinyin":"Wǒ men chū qù chī fàn ba.","english":"Let’s go out to eat","options":["Let’s cook at home","Let’s go out to eat","Let’s go shopping","Let’s drink tea"],"correctAnswer":1},
{"id":353,"sentence":"今天风很大。","pinyin":"Jīn tiān fēng hěn dà.","english":"It’s very windy today","options":["It’s very windy today","It’s very sunny today","It’s raining","It’s cold outside"],"correctAnswer":0},
{"id":354,"sentence":"别忘了带伞。","pinyin":"Bié wàng le dài sǎn.","english":"Don’t forget to bring an umbrella","options":["Don’t forget to bring an umbrella","Don’t forget to bring water","Don’t forget to sleep early","Don’t forget to eat"],"correctAnswer":0},
{"id":355,"sentence":"我马上回来。","pinyin":"Wǒ mǎ shàng huí lái.","english":"I’ll be right back","options":["I’ll go now","I’ll be right back","I’m not coming back","I’ll come tomorrow"],"correctAnswer":1},
{"id":356,"sentence":"这个地方很安全。","pinyin":"Zhè ge dì fang hěn ān quán.","english":"This place is very safe","options":["This place is very dangerous","This place is very safe","This place is crowded","This place is dirty"],"correctAnswer":1},
{"id":357,"sentence":"时间不早了。","pinyin":"Shí jiān bù zǎo le.","english":"It's getting late","options":["It’s still early","It’s getting late","It’s morning","It’s lunchtime"],"correctAnswer":1},
{"id":358,"sentence":"我们开始吧。","pinyin":"Wǒ men kāi shǐ ba.","english":"Let’s begin","options":["Let’s eat","Let’s go","Let’s begin","Let’s stop"],"correctAnswer":2},
{"id":359,"sentence":"他笑得很开心。","pinyin":"Tā xiào de hěn kāi xīn.","english":"He is laughing happily","options":["He is crying","He is angry","He is laughing happily","He is nervous"],"correctAnswer":2},
{"id":360,"sentence":"请关上门。","pinyin":"Qǐng guān shàng mén.","english":"Please close the door","options":["Please open the door","Please close the door","Please clean the room","Please wait outside"],"correctAnswer":1},
{"id":361,"sentence":"我需要帮助。","pinyin":"Wǒ xū yào bāng zhù.","english":"I need help","options":["I don’t need help","I need help","I can do it myself","I need money"],"correctAnswer":1},
{"id":362,"sentence":"你会开车吗？","pinyin":"Nǐ huì kāi chē ma?","english":"Can you drive?","options":["Can you drive?","Can you swim?","Can you fix this?","Can you speak English?"],"correctAnswer":0},
{"id":363,"sentence":"我要喝水。","pinyin":"Wǒ yào hē shuǐ.","english":"I want to drink water","options":["I want to drink water","I want to eat food","I want to sleep","I want to leave"],"correctAnswer":0},
{"id":364,"sentence":"这本书很好看。","pinyin":"Zhè běn shū hěn hǎo kàn.","english":"This book is very good","options":["This book is boring","This book is very good","This book is long","This book is expensive"],"correctAnswer":1},
{"id":365,"sentence":"手机没电了。","pinyin":"Shǒu jī méi diàn le.","english":"The phone is out of battery","options":["The phone is new","The phone is out of battery","The phone is broken","The phone is charging"],"correctAnswer":1},
{"id":366,"sentence":"我听不懂。","pinyin":"Wǒ tīng bù dǒng.","english":"I don't understand","options":["I don’t understand","I can hear you","I agree","I understand"],"correctAnswer":0},
{"id":367,"sentence":"他今天请假了。","pinyin":"Tā jīn tiān qǐng jià le.","english":"He took a leave today","options":["He is at work","He took a leave today","He is traveling","He is sick"],"correctAnswer":1},
{"id":368,"sentence":"灯还开着。","pinyin":"Dēng hái kāi zhe.","english":"The light is still on","options":["The light is still on","The light is off","The light is broken","The light is too bright"],"correctAnswer":0},
{"id":369,"sentence":"我没时间。","pinyin":"Wǒ méi shí jiān.","english":"I don't have time","options":["I don’t have time","I don’t want to go","I’m busy tomorrow","I have time"],"correctAnswer":0},
{"id":370,"sentence":"这道题很简单。","pinyin":"Zhè dào tí hěn jiǎn dān.","english":"This question is very easy","options":["This question is hard","This question is very easy","This question is long","This question is confusing"],"correctAnswer":1},
{"id":371,"sentence":"你住在哪里？","pinyin":"Nǐ zhù zài nǎ lǐ?","english":"Where do you live?","options":["Where do you work?","Where do you live?","Where are you now?","Where is your family?"],"correctAnswer":1},
{"id":372,"sentence":"水太烫了。","pinyin":"Shuǐ tài tàng le.","english":"The water is too hot","options":["The water is warm","The water is too hot","The water is cold","There is no water"],"correctAnswer":1},
{"id":373,"sentence":"请排队。","pinyin":"Qǐng pái duì.","english":"Please line up","options":["Please line up","Please sit down","Please come in","Please wait"],"correctAnswer":0},
{"id":374,"sentence":"我怕狗。","pinyin":"Wǒ pà gǒu.","english":"I’m afraid of dogs","options":["I don’t like cats","I like dogs","I’m afraid of dogs","I want a dog"],"correctAnswer":2},
{"id":375,"sentence":"今天我很忙。","pinyin":"Jīn tiān wǒ hěn máng.","english":"I’m very busy today","options":["I’m very busy today","I'm very tired today","I’m free today","I’m relaxing today"],"correctAnswer":0},
{"id":376,"sentence":"你要去哪儿？","pinyin":"Nǐ yào qù nǎ er?","english":"Where are you going?","options":["Where are you going?","What are you doing?","When are you leaving?","Who are you meeting?"],"correctAnswer":0},
{"id":377,"sentence":"我喜欢安静的地方。","pinyin":"Wǒ xǐ huan ān jìng de dì fang.","english":"I like quiet places","options":["I like quiet places","I like noisy places","I like crowded places","I like big places"],"correctAnswer":0},
{"id":378,"sentence":"你记得他吗？","pinyin":"Nǐ jì de tā ma?","english":"Do you remember him?","options":["Do you know him?","Do you remember him?","Do you miss him?","Do you like him?"],"correctAnswer":1},
{"id":379,"sentence":"快点儿！","pinyin":"Kuài diǎnr!","english":"Hurry up!","options":["Calm down","Hurry up!","Stop talking","Come here"],"correctAnswer":1},
{"id":380,"sentence":"这件衣服很便宜。","pinyin":"Zhè jiàn yī fu hěn pián yi.","english":"This piece of clothing is cheap","options":["This clothing is new","This clothing is cheap","This clothing is expensive","This clothing is dirty"],"correctAnswer":1},



{"id":381,"sentence":"我们会说中文。","pinyin":"Wǒ men dōu shuō zhōng wén.","english":"We can speak Chinese.","options":["We can speak Japanese","We can speak Chinese","We can speak French","We can speak English"],"correctAnswer":1},
{"id":382,"sentence":"他学中文五年了。","pinyin":"Tā xué zhōng wén wǔ nián le.","english":"He has been studying Chinese for five years.","options":["He has been studying Chinese for three years","He has been studying Chinese for ten years","He has been studying Chinese for five years","He has been studying Chinese for one year"],"correctAnswer":2},
{"id":383,"sentence":"你吃午饭了吗？","pinyin":"Nǐ chī wǔ fàn le ma?","english":"Did you have lunch?","options":["Did you have breakfast?","Are you having lunch?","Did you have lunch?","Did you have dinner?"],"correctAnswer":2},
{"id":384,"sentence":"他的房子朝西。","pinyin":"Tā de fáng zi cháo xī.","english":"His house faces west.","options":["His house faces south","His house faces west","His house faces north","His house faces east"],"correctAnswer":1},
{"id":385,"sentence":"医院在学校西边。","pinyin":"Yī yuàn zài xué xiào xī bian.","english":"The hospital is on the west side of the school.","options":["The hospital is on the north side of the school","The hospital is on the west side of the school","The hospital is on the east side of the school","The hospital is on the south side of the school"],"correctAnswer":1},
{"id":386,"sentence":"你可以帮我洗车吗？","pinyin":"Nǐ kě yǐ bāng wǒ xǐ chē ma?","english":"Can you wash my car for me?","options":["Can you wash my bike for me?","Can you cook for me?","Can you wash my car for me?","Can you clean my room for me?"],"correctAnswer":2},
{"id":387,"sentence":"洗手间在二楼。","pinyin":"Xǐ shǒu jiān zài èr lóu.","english":"The washroom is on the second floor.","options":["The washroom is on the third floor","The washroom is on the second floor","The washroom is outside","The washroom is on the first floor"],"correctAnswer":1},
{"id":388,"sentence":"你喜欢吃什么？","pinyin":"Nǐ xǐ huan chī shén me?","english":"What do you like to eat?","options":["What is your favorite sport?","What do you like to eat?","What is your favorite color?","What do you like to drink?"],"correctAnswer":1},
{"id":389,"sentence":"你下飞机了吗？","pinyin":"Nǐ xià fēi jī le ma?","english":"Did you get off the plane?","options":["Did you get on the plane?","Did you leave the airport?","Did you get off the plane?","Did you enter the airport?"],"correctAnswer":2},
{"id":390,"sentence":"你几点下班？","pinyin":"Nǐ jǐ diǎn xià bān?","english":"What time do you get off work?","options":["What time do you wake up?","What time do you start work?","What time do you finish class?","What time do you get off work?"],"correctAnswer":3},
{"id":391,"sentence":"你的笔在桌子下边。","pinyin":"Nǐ de bǐ zài zhuō zi xià bian.","english":"Your pen is under the table.","options":["Your pen is on the table","Your pen is in the drawer","Your pen is under the table","Your pen is next to the table"],"correctAnswer":2},
{"id":392,"sentence":"我在下一个路口下车。","pinyin":"Wǒ zài xià yí gè lù kǒu xià chē.","english":"I get off at the next intersection.","options":["I get on at the next intersection","I get off at the next intersection","I get off at the last stop","I get on at the last stop"],"correctAnswer":1},
{"id":393,"sentence":"下次见！","pinyin":"Xià cì jiàn!","english":"See you next time!","options":["Goodbye!","See you next time!","See you yesterday!","Hello!"],"correctAnswer":1},
{"id":394,"sentence":"你今天几点下课？","pinyin":"Nǐ jīn tiān jǐ diǎn xià kè?","english":"What time do you finish class today?","options":["What time do you finish class today?","What time is lunch today?","What time do you wake up today?","What time do you start class today?"],"correctAnswer":0},
{"id":395,"sentence":"你下午有空吗？","pinyin":"Nǐ xià wǔ yǒu kòng ma?","english":"Are you free this afternoon?","options":["Are you free this afternoon?","Are you busy this afternoon?","Are you free this evening?","Are you free this morning?"],"correctAnswer":0},
{"id":396,"sentence":"明天会下雨。","pinyin":"Míng tiān huì xià yǔ.","english":"It will rain tomorrow.","options":["It will snow tomorrow","It will be sunny tomorrow","It will rain tomorrow","It will be cloudy tomorrow"],"correctAnswer":2},
{"id":397,"sentence":"我们先做作业，再看电视。","pinyin":"Wǒ men xiān zuò zuò yè, zài kàn diàn shì.","english":"We do our homework first and then watch TV.","options":["We eat first and then do homework","We do our homework first and then watch TV","We sleep first and then watch TV","We watch TV first and then do homework"],"correctAnswer":1},
{"id":398,"sentence":"你是高先生吗？","pinyin":"Nǐ shì gāo xiān sheng ma?","english":"Are you Mr. Gao?","options":["Are you Mr. Wang?","Are you Mr. Chen?","Are you Mr. Gao?","Are you Mr. Li?"],"correctAnswer":2},
{"id":399,"sentence":"现在几点？","pinyin":"Xiàn zài jǐ diǎn?","english":"What time is it now?","options":["What time is your class?","What time is lunch?","What time was it yesterday?","What time is it now?"],"correctAnswer":3},
{"id":400,"sentence":"我需要想一下。","pinyin":"Wǒ xū yào xiǎng yí xià.","english":"I need to think about it.","options":["I need to sleep now","I need to do it now","I need to think about it","I need to eat now"],"correctAnswer":2},



{"id":401,"sentence":"我的家很小。","pinyin":"Wǒ de jiā hěn xiǎo.","english":"My home is small.","options":["My home is new","My home is beautiful","My home is small","My home is big"],"correctAnswer":2},
{"id":402,"sentence":"你有小孩儿吗？","pinyin":"Nǐ yǒu xiǎo háir ma?","english":"Do you have children?","options":["Do you have siblings?","Do you have children?","Do you have pets?","Do you have friends?"],"correctAnswer":1},
{"id":403,"sentence":"这是赵小姐。","pinyin":"Zhè shì Zhào xiǎo jiě.","english":"This is Miss Zhao.","options":["This is Mr. Zhao","This is Miss Zhao","This is Mrs. Zhao","This is Ms. Wang"],"correctAnswer":1},
{"id":404,"sentence":"那个小朋友很可爱。","pinyin":"Nà gè xiǎo péng you hěn kě ài.","english":"That kid is so cute.","options":["That kid is naughty","That kid is very tall","That kid is so cute","That kid is sad"],"correctAnswer":2},
{"id":405,"sentence":"你每天工作几个小时？","pinyin":"Nǐ měi tiān gōng zuò jǐ gè xiǎo shí?","english":"How many hours do you work per day?","options":["How many hours do you study","How many hours do you work per day","How many hours do you sleep","How many hours do you play"],"correctAnswer":1},
{"id":406,"sentence":"她是小学老师。","pinyin":"Tā shì xiǎo xué lǎo shī.","english":"She is an elementary school teacher.","options":["She is a student","She is a college professor","She is a middle school teacher","She is an elementary school teacher"],"correctAnswer":3},
{"id":407,"sentence":"那个小学生很高。","pinyin":"Nà gè xiǎo xué shēng hěn gāo.","english":"That elementary school student is tall.","options":["That elementary school student is tall","That elementary school student is smart","That elementary school student is short","That elementary school student is young"],"correctAnswer":0},
{"id":408,"sentence":"他在笑什么？","pinyin":"Tā zài xiào shén me?","english":"What is he laughing at?","options":["Why is he crying","Why is he sleeping","What is he laughing at","What is he doing"],"correctAnswer":2},
{"id":409,"sentence":"你会写汉字吗？","pinyin":"Nǐ huì xiě hàn zì ma?","english":"Can you write Chinese characters?","options":["Can you write Chinese characters","Can you draw pictures","Can you read Chinese characters","Can you speak Chinese"],"correctAnswer":0},
{"id":410,"sentence":"谢谢！","pinyin":"Xiè xie!","english":"Thank you!","options":["You're welcome!","Thank you!","Goodbye!","Sorry!"],"correctAnswer":1},
{"id":411,"sentence":"这是你的新手机吗？","pinyin":"Zhè shì nǐ de xīn shǒu jī ma?","english":"Is this your new phone?","options":["Is this your friend's phone","Is this a broken phone","Is this your old phone","Is this your new phone"],"correctAnswer":3},
{"id":412,"sentence":"新年快乐！","pinyin":"Xīn nián kuài lè!","english":"Happy New Year!","options":["Happy Birthday!","Merry Christmas!","Happy New Year!","Good Night!"],"correctAnswer":2},
{"id":413,"sentence":"我下个星期要搬家。","pinyin":"Wǒ xià gè xīng qī yào bān jiā.","english":"I'm moving next week.","options":["I'm staying home next week","I'm traveling next week","I'm working next week","I'm moving next week"],"correctAnswer":3},
{"id":414,"sentence":"我这个星期日有中文课。","pinyin":"Wǒ zhè gè xīng qī rì yǒu zhōng wén kè.","english":"I have Chinese class this Sunday.","options":["I have English class this Sunday","I have Chinese class this Sunday","I have no class this Sunday","I have math class this Sunday"],"correctAnswer":1},
{"id":415,"sentence":"你这个星期天有空吗？","pinyin":"Nǐ zhè gè xīng qī tiān yǒu kòng ma?","english":"Are you free this Sunday?","options":["Are you free this Sunday","Are you busy this Sunday","Are you traveling this Sunday","Are you studying this Sunday"],"correctAnswer":0},
{"id":416,"sentence":"行吗？","pinyin":"Xíng ma?","english":"Is it OK?","options":["Should I wait?","Is it not OK?","Is it OK?","Can I go?"],"correctAnswer":2},
{"id":417,"sentence":"你要休息吗？","pinyin":"Nǐ yào xiū xi ma?","english":"Do you want to rest?","options":["Do you want to eat?","Do you want to work?","Do you want to study?","Do you want to rest?"],"correctAnswer":3},
{"id":418,"sentence":"你学中文多久了？","pinyin":"Nǐ xué zhōng wén duō jiǔ le?","english":"How long have you been studying Chinese?","options":["How long have you been studying Chinese","How long have you been learning English","How long have you been working","How long have you been traveling"],"correctAnswer":0},
{"id":419,"sentence":"他是一个好学生。","pinyin":"Tā shì yí gè hǎo xué sheng.","english":"He is a good student.","options":["He is a good student","He is a smart student","He is a tall student","He is a bad student"],"correctAnswer":0},
{"id":420,"sentence":"你想学习吗？","pinyin":"Nǐ xiǎng xué xí ma?","english":"Do you want to study?","options":["Do you want to eat?","Do you want to play?","Do you want to study?","Do you want to sleep?"],"correctAnswer":2},


{"id":421,"sentence":"这个学校怎么样？","pinyin":"Zhè gè xué xiào zěn me yàng?","english":"How is this school?","options":["How is this teacher?","How is this city?","How is this student?","How is this school?"],"correctAnswer":3},
{"id":422,"sentence":"这个学院大吗？","pinyin":"Zhè gè xué yuàn dà ma?","english":"Is this college big?","options":["Is this school small?","Is this college big?","Is this college small?","Is this school big?"],"correctAnswer":1},
{"id":423,"sentence":"你要吃巧克力吗？","pinyin":"Nǐ yào chī qiǎo kè lì ma?","english":"Do you want some chocolate?","options":["Do you want some cake?","Do you want some chocolate?","Do you want some candy?","Do you want some fruit?"],"correctAnswer":1},
{"id":424,"sentence":"我爷爷退休了。","pinyin":"Wǒ yé ye tuì xiū le.","english":"My grandpa is retired.","options":["My grandpa is retired","My grandpa is sick","My grandpa is traveling","My grandpa is working"],"correctAnswer":0},
{"id":425,"sentence":"我也喜欢跳舞。","pinyin":"Wǒ yě xǐ huan tiào wǔ.","english":"I also like to dance.","options":["I like to sing","I also like to dance","I like to read","I like to play sports"],"correctAnswer":1},
{"id":426,"sentence":"第几页？","pinyin":"Dì jǐ yè?","english":"Which page?","options":["Which book?","Which page?","What line?","What chapter?"],"correctAnswer":1},
{"id":427,"sentence":"利息率是百分之一。","pinyin":"Lì xī lǜ shì bǎi fēn zhī yī.","english":"The interest rate is one percent.","options":["The interest rate is ten percent","The interest rate is zero percent","The interest rate is one percent","The interest rate is five percent"],"correctAnswer":2},
{"id":428,"sentence":"这件衣服的质量很好。","pinyin":"Zhè jiàn yī fu de zhì liàng hěn hǎo.","english":"The quality of these clothes is good.","options":["The clothes are small","The quality of these clothes is good","The clothes are expensive","The quality of these clothes is bad"],"correctAnswer":1},
{"id":429,"sentence":"他是医生。","pinyin":"Tā shì yī shēng.","english":"He is a doctor.","options":["He is a student","He is a doctor","He is a nurse","He is a teacher"],"correctAnswer":1},
{"id":430,"sentence":"附近有医院吗？","pinyin":"Fù jìn yǒu yī yuàn ma?","english":"Is there a hospital nearby?","options":["Is there a school nearby?","Is there a shop nearby?","Is there a park nearby?","Is there a hospital nearby?"],"correctAnswer":3},
{"id":431,"sentence":"这是你的一半。","pinyin":"Zhè shì nǐ de yí bàn.","english":"This is your half.","options":["This is your part","This is your half","This is your whole","This is your share"],"correctAnswer":1},
{"id":432,"sentence":"请等一会儿。","pinyin":"Qǐng děng yí huìr.","english":"Please wait a moment.","options":["Please go out","Please wait a moment","Please hurry","Please come in"],"correctAnswer":1},
{"id":433,"sentence":"我们一块儿玩吧！","pinyin":"Wǒ men yí kuàir wán ba!","english":"Let's play together!","options":["Let's study together","Let's play together","Let's eat together","Let's walk together"],"correctAnswer":1},
{"id":434,"sentence":"你可以照顾一下儿宝宝吗？","pinyin":"Nǐ kě yǐ zhào gù yí xiàr bǎo bǎo ma?","english":"Can you look after the baby for a bit?","options":["Can you play with the baby?","Can you feed the baby?","Can you look after the baby for a bit?","Can you wash the baby?"],"correctAnswer":2},
{"id":435,"sentence":"他们一样高。","pinyin":"Tā men yí yàng gāo.","english":"They are the same height.","options":["They are different heights","They are short","They are tall","They are the same height"],"correctAnswer":3},
{"id":436,"sentence":"她的头发一边长，一边短。","pinyin":"Tā de tóu fa yì biān cháng, yì biān duǎn.","english":"Her hair is long on one side and short on the other.","options":["Her hair is long on one side and short on the other","Her hair is curly","Her hair is long","Her hair is short"],"correctAnswer":0},
{"id":437,"sentence":"我会说一点儿中文。","pinyin":"Wǒ huì shuō yī diǎnr zhōng wén.","english":"I can speak a little bit Chinese.","options":["I cannot speak","I can speak a little bit Chinese","I can speak fluently","I can write Chinese"],"correctAnswer":1},
{"id":438,"sentence":"我们一起去旅行吧！","pinyin":"Wǒ men yì qǐ qù lǚ xíng ba!","english":"Let's travel together!","options":["Let's study together","Let's work together","Let's travel together","Let's eat together"],"correctAnswer":2},
{"id":439,"sentence":"他买了一些衣服。","pinyin":"Tā mǎi le yì xiē yī fu.","english":"He bought some clothes.","options":["He bought some books","He bought some toys","He bought some food","He bought some clothes"],"correctAnswer":3},
{"id":440,"sentence":"你会用筷子吗？","pinyin":"Nǐ huì yòng kuài zi ma?","english":"Can you use chopsticks?","options":["Can you use chopsticks?","Can you use a fork?","Can you use a spoon?","Can you use a knife?"],"correctAnswer":0},


{"id":451,"sentence":"你家离地铁站远吗？","pinyin":"Nǐ jiā lí dì tiě zhàn yuǎn ma?","english":"Is your home far from the metro station?","options":["Is your office far from the metro station?","Is your school far from the metro station?","Is your home far from the metro station?","Is your home near the metro station?"],"correctAnswer":2},
{"id":452,"sentence":"他学中文六个月了。","pinyin":"Tā xué zhōng wén liù gè yuè le.","english":"He has been learning Chinese for 6 months.","options":["He has been learning Chinese for 6 months","He has been learning Chinese for 3 months","He has been learning Chinese for 6 years","He has been learning Chinese for 1 year"],"correctAnswer":0},
{"id":453,"sentence":"再做一次。","pinyin":"Zài zuò yí cì.","english":"Do it again.","options":["Stop doing it","Do it later","Do it again","Do it now"],"correctAnswer":2},
{"id":454,"sentence":"再见！","pinyin":"Zài jiàn!","english":"Goodbye!","options":["See you later!","Goodbye!","Hello!","Good night!"],"correctAnswer":1},
{"id":455,"sentence":"你在办公室吗？","pinyin":"Nǐ zài bàn gōng shì ma?","english":"Are you in the office?","options":["Are you at school?","Are you at home?","Are you outside?","Are you in the office?"],"correctAnswer":3},
{"id":456,"sentence":"你在家吗？","pinyin":"Nǐ zài jiā ma?","english":"Are you at home?","options":["Are you at school?","Are you at work?","Are you at home?","Are you outside?"],"correctAnswer":2},
{"id":457,"sentence":"我要早睡早起。","pinyin":"Wǒ yào zǎo shuì zǎo qǐ.","english":"I want to go to bed early and get up early.","options":["I want to sleep in the afternoon","I want to go to bed early and get up early","I want to stay up late and sleep late","I want to sleep during the day"],"correctAnswer":1},
{"id":458,"sentence":"你早饭吃了什么？","pinyin":"Nǐ zǎo fàn chī le shén me?","english":"What did you eat for breakfast?","options":["What did you eat for dinner?","What did you eat for lunch?","What did you eat for breakfast?","Did you eat breakfast?"],"correctAnswer":2},
{"id":459,"sentence":"早上好！","pinyin":"Zǎo shang hǎo!","english":"Good morning!","options":["Good evening!","Good night!","Good afternoon!","Good morning!"],"correctAnswer":3},
{"id":460,"sentence":"你知道怎么做饺子吗？","pinyin":"Nǐ zhī dào zěn me zuò jiǎo zi ma?","english":"Do you know how to make dumplings?","options":["Do you know how to make dumplings?","Do you know how to make rice?","Do you know how to make noodles?","Do you know how to cook soup?"],"correctAnswer":0},
{"id":461,"sentence":"我在火车站等你。","pinyin":"Wǒ zài huǒ chē zhàn děng nǐ.","english":"I'm waiting for you at the train station.","options":["I'm waiting for you at the airport","I'm waiting for you at school","I'm waiting for you at the train station","I'm waiting for you at home"],"correctAnswer":2},
{"id":462,"sentence":"我在找我的手机。","pinyin":"Wǒ zài zhǎo wǒ de shǒu jī.","english":"I'm looking for my phone.","options":["I'm looking for my keys","I'm looking for my wallet","I'm looking for my bag","I'm looking for my phone"],"correctAnswer":3},
{"id":463,"sentence":"你找到工作了吗？","pinyin":"Nǐ zhǎo dào gōng zuò le ma?","english":"Have you found a job?","options":["Have you found a friend?","Have you found a job?","Have you found your book?","Have you found your phone?"],"correctAnswer":1},
{"id":464,"sentence":"这是我的手机。","pinyin":"Zhè shì wǒ de shǒu jī.","english":"This is my cell phone.","options":["This is my tablet","This is my laptop","This is my wallet","This is my cell phone"],"correctAnswer":3},
{"id":465,"sentence":"你的教室在这边。","pinyin":"Nǐ de jiào shì zài zhè biān.","english":"Your classroom is here.","options":["Your home is here","Your school is here","Your office is here","Your classroom is here"],"correctAnswer":3},
{"id":466,"sentence":"这里的菜很好吃。","pinyin":"Zhè lǐ de cài hěn hǎo chī.","english":"The food here is delicious.","options":["The food here is spicy","The food here is cold","The food here is delicious","The food here is expensive"],"correctAnswer":2},
{"id":467,"sentence":"我常常在这儿健身。","pinyin":"Wǒ cháng cháng zài zhèr jiàn shēn.","english":"I often work out here.","options":["I often sleep here","I often eat here","I often read here","I often work out here"],"correctAnswer":3},
{"id":468,"sentence":"这些甜点都是你做的吗？","pinyin":"Zhè xiē tián diǎn dōu shì nǐ zuò de ma?","english":"Did you make all these desserts?","options":["Did you buy all these desserts?","Did you make all these desserts?","Did someone else make the desserts?","Did you eat all these desserts?"],"correctAnswer":1},
{"id":469,"sentence":"他站着。","pinyin":"Tā zhàn zhe.","english":"He is standing.","options":["He is lying down","He is sitting","He is running","He is standing"],"correctAnswer":3},
{"id":470,"sentence":"你真聪明。","pinyin":"Nǐ zhēn cōng ming.","english":"You are really smart.","options":["You are really tall","You are really strong","You are really kind","You are really smart"],"correctAnswer":3},
{"id":471,"sentence":"这新闻是真的吗？","pinyin":"Zhè xīn wén shì zhēn de ma?","english":"Is this news true?","options":["Is this news fake?","Is this news true?","Is this news old?","Is this news interesting?"],"correctAnswer":1},
{"id":472,"sentence":"我正开车呢。","pinyin":"Wǒ zhèng kāi chē ne.","english":"I am driving.","options":["I am walking","I am running","I am eating","I am driving"],"correctAnswer":3},
{"id":473,"sentence":"我正在健身。","pinyin":"Wǒ zhèng zài jiàn shēn.","english":"I'm working out.","options":["I'm sleeping","I'm studying","I'm working out","I'm resting"],"correctAnswer":2},
{"id":474,"sentence":"我不知道。","pinyin":"Wǒ bù zhī dào.","english":"I don't know.","options":["I know","I don't know","I forgot","I understand"],"correctAnswer":1},
{"id":475,"sentence":"他的历史知识很浅薄。","pinyin":"Tā de lì shǐ zhī shi hěn qiǎn bó.","english":"His historical knowledge is shallow.","options":["His historical knowledge is excellent","His historical knowledge is deep","His historical knowledge is shallow","His historical knowledge is average"],"correctAnswer":2},
{"id":476,"sentence":"她在电影中演一个妈妈。","pinyin":"Tā zài diàn yǐng zhōng yǎn yí gè mā ma.","english":"She plays a mom in the movie.","options":["She plays a student in the movie","She plays a teacher in the movie","She plays a doctor in the movie","She plays a mom in the movie"],"correctAnswer":3},
{"id":477,"sentence":"你去过中国吗？","pinyin":"Nǐ qù guò zhōng guó ma?","english":"Have you been to China?","options":["Have you been to Europe?","Have you been to America?","Have you been to China?","Have you been to Japan?"],"correctAnswer":2},
{"id":478,"sentence":"我的车停在中间。","pinyin":"Wǒ de chē tíng zài zhōng jiān.","english":"My car is parked in the middle.","options":["My car is parked on the side","My car is parked at the front","My car is parked behind","My car is parked in the middle"],"correctAnswer":3},
{"id":479,"sentence":"你的中文怎么样？","pinyin":"Nǐ de zhōng wén zěn me yàng?","english":"How is your Chinese?","options":["How is your math?","How is your Chinese?","How is your English?","How is your reading?"],"correctAnswer":1},
{"id":480,"sentence":"我们中午一起吃午饭吧！","pinyin":"Wǒ men zhōng wǔ yī qǐ chī wǔ fàn ba!","english":"Let's have lunch together at noon!","options":["Let's have a snack together","Let's have lunch together at noon","Let's have breakfast together","Let's have dinner together"],"correctAnswer":1},
{"id":481,"sentence":"他是中学老师。","pinyin":"Tā shì zhōng xué lǎo shī.","english":"He is a middle school teacher.","options":["He is a college teacher","He is a middle school teacher","He is an elementary school teacher","He is a university professor"],"correctAnswer":1},
{"id":482,"sentence":"那个中学生很高。","pinyin":"Nà gè zhōng xué shēng hěn gāo.","english":"That middle school student is tall.","options":["That middle school student is smart","That middle school student is short","That middle school student is tall","That middle school student is young"],"correctAnswer":2},
{"id":483,"sentence":"我的行李很重。","pinyin":"Wǒ de xíng lǐ hěn zhòng.","english":"My luggage is heavy.","options":["My luggage is small","My luggage is heavy","My luggage is big","My luggage is light"],"correctAnswer":1},
{"id":484,"sentence":"汉语声调很重要。","pinyin":"Hàn yǔ shēng diào hěn zhòng yào.","english":"Chinese tones are very important.","options":["Chinese grammar is very important","Chinese tones are very important","Chinese vocabulary is very important","Chinese writing is very important"],"correctAnswer":1},
{"id":485,"sentence":"你住在哪里？","pinyin":"Nǐ zhù zài nǎ lǐ?","english":"Where do you live?","options":["Where do you go shopping?","Where do you study?","Where do you live?","Where do you work?"],"correctAnswer":2},
{"id":486,"sentence":"我要准备晚饭。","pinyin":"Wǒ yào zhǔn bèi wǎn fàn.","english":"I'm going to prepare dinner.","options":["I'm going to prepare lunch","I'm going to prepare breakfast","I'm going to prepare dinner","I'm going to prepare dessert"],"correctAnswer":2},
{"id":487,"sentence":"这张桌子多长？","pinyin":"Zhè zhāng zhuō zi duō cháng?","english":"How long is this table?","options":["How heavy is this table?","How long is this table?","How wide is this table?","How tall is this table?"],"correctAnswer":1},
{"id":488,"sentence":"这是什么字？","pinyin":"Zhè shì shén me zì?","english":"What character is this?","options":["What number is this?","What word is this?","What character is this?","What sentence is this?"],"correctAnswer":2},
{"id":489,"sentence":"请给我一把刀子和叉子。","pinyin":"Qǐng gěi wǒ yī bǎ dāo zi hé chā zi.","english":"Please give me a knife and fork.","options":["Please give me a cup and spoon","Please give me chopsticks and bowl","Please give me a knife and fork","Please give me a spoon and plate"],"correctAnswer":2},
{"id":490,"sentence":"走吧！","pinyin":"Zǒu ba!","english":"Let's go!","options":["Stop!","Wait!","Let's go!","Come here!"],"correctAnswer":2},
{"id":491,"sentence":"他常常走路去学校。","pinyin":"Tā cháng cháng zǒu lù qù xué xiào.","english":"He often walks to school.","options":["He often drives to school","He often walks to school","He often takes the bus to school","He often bikes to school"],"correctAnswer":1},
{"id":492,"sentence":"你最喜欢哪个季节？","pinyin":"Nǐ zuì xǐ huan nǎ gè jì jié?","english":"Which season do you like the most?","options":["Which holiday do you like the most?","Which day do you like the most?","Which season do you like the most?","Which month do you like the most?"],"correctAnswer":2},
{"id":493,"sentence":"你最好的朋友是谁？","pinyin":"Nǐ zuì hǎo de péng you shì shéi?","english":"Who is your best friend?","options":["Who is your teacher?","Who is your classmate?","Who is your neighbor?","Who is your best friend?"],"correctAnswer":3},
{"id":494,"sentence":"今天是最后一天。","pinyin":"Jīn tiān shì zuì hòu yī tiān.","english":"Today is the last day.","options":["Today is a holiday","Today is Monday","Today is the first day","Today is the last day"],"correctAnswer":3},
{"id":495,"sentence":"你昨天加班了吗？","pinyin":"Nǐ zuó tiān jiā bān le ma?","english":"Did you work overtime yesterday?","options":["Did you work yesterday?","Did you work overtime yesterday?","Did you rest yesterday?","Did you study yesterday?"],"correctAnswer":1},
{"id":496,"sentence":"你用左手写字吗？","pinyin":"Nǐ yòng zuǒ shǒu xiě zì ma?","english":"Do you write with your left hand?","options":["Do you write with your left hand?","Do you write with your right hand?","Do you type with your right hand?","Do you type with your left hand?"],"correctAnswer":0},
{"id":497,"sentence":"停车场在超市的左边。","pinyin":"Tíng chē chǎng zài chāo shì de zuǒ bian.","english":"The parking lot is on the left side of the supermarket.","options":["The parking lot is in front of the supermarket","The parking lot is on the right side of the supermarket","The parking lot is on the left side of the supermarket","The parking lot is behind the supermarket"],"correctAnswer":2},
{"id":498,"sentence":"我可以坐在这里吗？","pinyin":"Wǒ kě yǐ zuò zài zhè lǐ ma?","english":"Can I sit here?","options":["Can I stand here?","Can I wait here?","Can I lie here?","Can I sit here?"],"correctAnswer":3},
{"id":499,"sentence":"我们坐下喝杯茶吧。","pinyin":"Wǒ men zuò xià hē bēi chá ba.","english":"Let's sit down and have a cup of tea.","options":["Let's walk and have a cup of tea","Let's lie down and have a cup of tea","Let's sit down and have a cup of tea","Let's stand and have a cup of tea"],"correctAnswer":2},
{"id":500,"sentence":"你下班后要做什么？","pinyin":"Nǐ xià bān hòu yào zuò shén me?","english":"What are you going to do after work?","options":["What did you do after work?","What are you doing at work?","What are you going to do after work?","What will you do tomorrow?"],"correctAnswer":2}

]

@sentence_bp.route('/quiz')
def sentence_quiz():
    """Render the sentence quiz page"""
    return render_template('quiz_sentences.html')

@sentence_bp.route('/api/quiz-sentences')
def get_quiz_sentences():
    """API endpoint to get sentences for the quiz - FIXED VERSION"""
    try:
        # Get number of questions from request (default 20)
        num_questions = int(request.args.get('count', 20))
        
        # Select random sentences for the quiz
        quiz_sentences = random.sample(HSK1_SENTENCES, min(num_questions, len(HSK1_SENTENCES)))
        
        # Create a deep copy and randomize the position of correct answers
        randomized_sentences = []
        
        for sentence in quiz_sentences:
            # Create a deep copy to avoid modifying the original data
            sentence_copy = sentence.copy()
            sentence_copy['options'] = sentence['options'].copy()
            
            # ALWAYS use the 'english' field as the correct answer, IGNORE correctAnswer field
            correct_answer_text = sentence['english']
            
            # Randomize options
            random.shuffle(sentence_copy['options'])
            
            # Find the new position of the correct answer using the 'english' field
            try:
                # First try exact match
                new_correct_index = sentence_copy['options'].index(correct_answer_text)
            except ValueError:
                # If exact match fails, try case-insensitive matching
                new_correct_index = 0
                for i, option in enumerate(sentence_copy['options']):
                    if option.lower().strip() == correct_answer_text.lower().strip():
                        new_correct_index = i
                        break
            
            sentence_copy['correctAnswer'] = new_correct_index
            
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
    """API endpoint to get a new quiz with different sentences - FIXED VERSION"""
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
            # Create a deep copy
            sentence_copy = sentence.copy()
            sentence_copy['options'] = sentence['options'].copy()
            
            # ALWAYS use the 'english' field as the correct answer, IGNORE correctAnswer field
            correct_answer_text = sentence['english']
            
            # Randomize options
            random.shuffle(sentence_copy['options'])
            
            # Find the new position of the correct answer using the 'english' field
            try:
                # First try exact match
                new_correct_index = sentence_copy['options'].index(correct_answer_text)
            except ValueError:
                # If exact match fails, try case-insensitive matching
                new_correct_index = 0
                for i, option in enumerate(sentence_copy['options']):
                    if option.lower().strip() == correct_answer_text.lower().strip():
                        new_correct_index = i
                        break
            
            sentence_copy['correctAnswer'] = new_correct_index
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

@sentence_bp.route('/api/debug-sentence/<int:sentence_id>')
def debug_sentence(sentence_id):
    """Debug endpoint to check a specific sentence"""
    try:
        sentence = next((s for s in HSK1_SENTENCES if s['id'] == sentence_id), None)
        
        if sentence:
            return jsonify({
                'success': True,
                'sentence': sentence,
                'debug_info': {
                    'correct_answer_from_data': sentence.get('correctAnswer'),
                    'english_field': sentence.get('english'),
                    'expected_correct_option': sentence['options'][sentence['correctAnswer']] if sentence.get('correctAnswer') is not None and 0 <= sentence['correctAnswer'] < len(sentence['options']) else 'INVALID INDEX',
                    'options_count': len(sentence['options'])
                }
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