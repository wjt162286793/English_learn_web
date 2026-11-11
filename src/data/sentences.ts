import type { SentenceGroup, SentenceItem } from '../types/course'

function parseGroup(id: string, titleEn: string, titleZh: string, raw: string): SentenceGroup {
  const items: SentenceItem[] = []

  for (const rawLine of raw.split('\n')) {
    const line = rawLine.trim()
    if (line.length === 0) {
      continue
    }

    const match = /^(\d+)\.\s*(.+)\s+—\s+(.+)$/.exec(line)
    if (!match) {
      continue
    }

    items.push({
      id: `${id}-s${match[1]}`,
      textEn: match[2],
      note: match[3],
    })
  }

  return { id, titleEn, titleZh, items }
}

const unit1Raw = `1. My family lives in a small **apartment** near the park. — apartment 公寓 n.
2. My uncle is very **generous**; he always pays for dinner. — generous 慷慨的 adj.
3. Grandpa loves telling jokes — he has a great sense of **humor**. — humor 幽默 n.
4. Can you **describe** your best friend in three words? — describe 描述 v.
5. The boy **confessed** that he had broken the window. — confess 坦白 v.
6. My father will **retire** next year at sixty. — retire 退休 v.
7. Reading every day is a good way to **improve** your English. — improve 改进 v.
8. If you have a legal problem, you should ask a **lawyer**. — lawyer 律师 n.
9. The **engineer** designed a new bridge for the city. — engineer 工程师 n.
10. My cousin is training to become a **pilot**. — pilot 飞行员 n.
11. It took a lot of **courage** to tell her the truth. — courage 勇气 n.
12. Don't judge people by their **appearance**. — appearance 外貌 n.
13. She is **allergic** to seafood, so she never eats shrimp. — allergic 过敏的 adj.
14. Children should learn to **respect** older people. — respect 尊重 v./n.
15. My neighbor, a **widow**, lives alone with her cat. — widow 寡妇 n.
16. Her **character** is gentle but strong. — character 性格 n.
17. Tom is **reliable** — if he promises, he will do it. — reliable 可靠的 adj.
18. My parents are very **supportive** of my choice. — supportive 支持的 adj.
19. **Curious** children ask questions all day long. — curious 好奇的 adj.
20. The old man lives on a small **pension**. — pension 养老金 n.
21. My grandmother **raised** five children by herself. — raise 养育 v.
22. We can't **afford** a big house in this city. — afford 承担得起 v.
23. I **prefer** walking to taking the bus. — prefer 更喜欢 v.
24. He has a very positive **attitude** toward life. — attitude 态度 n.
25. His brother is **addicted** to video games. — addicted 上瘾的 adj.
26. The young **couple** next door just got married. — couple 夫妇 n.
27. They announced their **engagement** last Sunday. — engagement 订婚 n.
28. After years of arguing, they decided to **divorce**. — divorce 离婚 v./n.
29. I have two **siblings**: an elder brother and a younger sister. — sibling 兄弟姐妹 n.
30. My little **niece** is only three years old. — niece 侄女；外甥女 n.
31. Our **ancestors** lived in this village 200 years ago. — ancestor 祖先 n.
32. I spent a happy **childhood** in the countryside. — childhood 童年 n.
33. She spent her **youth** studying abroad. — youth 青年时期 n.
34. He is **easygoing**, so everyone likes him. — easygoing 随和的 adj.
35. Don't be so **selfish** — share the cake with your sister. — selfish 自私的 adj.
36. Her smile is warm and **sincere**. — sincere 真诚的 adj.
37. Although he is famous, he stays **humble**. — humble 谦虚的 adj.
38. A **loyal** friend stands by you in hard times. — loyal 忠诚的 adj.
39. She is highly **intelligent** and learns very fast. — intelligent 聪明的 adj.
40. You are old enough to be **responsible** for your own actions. — responsible 负责的 adj.
41. My aunt works as a **maid** in a rich family. — maid 女佣 n.
42. The new **chef** cooks wonderful Italian food. — chef 主厨 n.
43. I go to the **dentist** twice a year. — dentist 牙医 n.
44. Every morning he **jogs** around the lake. — jog 慢跑 v.
45. My mother does **yoga** to stay relaxed. — yoga 瑜伽 n.
46. He is too **stubborn** to change his mind. — stubborn 固执的 adj.
47. Speak to the children in a **gentle** voice. — gentle 温柔的 adj.
48. Why did he **betray** his best friend? — betray 背叛 v.
49. Everyone needs a little **privacy**, even at home. — privacy 隐私 n.
50. She **graduated** from Peking University in 2020. — graduate 毕业 v.`

const unit2Raw = `1. Cleaning the house on weekends is my least favorite **chore**. — chore 家务杂事 n.
2. Mom does the **laundry** every Saturday morning. — laundry 洗衣；待洗衣物 n.
3. I **vacuum** the carpet twice a week. — vacuum 用吸尘器打扫 v.
4. He **mopped** the wet kitchen floor. — mop 拖地 v.
5. Learn to **iron** your own shirts. — iron 熨烫 v.
6. The **faucet** is dripping; can you fix it? — faucet 水龙头 n.
7. She boiled water in the **kettle** for tea. — kettle 水壶 n.
8. Put the meat in the **freezer** to keep it fresh. — freezer 冷冻室 n.
9. Grandpa sweeps the yard with an old **broom**. — broom 扫帚 n.
10. Please **dust** the shelves — they're full of dirt. — dust 掸灰 v.
11. Let me **tidy** up my desk before dinner. — tidy 收拾 v.
12. I have a few **errands** to run downtown. — errand 差事；跑腿 n.
13. We need to buy some **groceries** on the way home. — grocery 食品杂货 n.
14. Keep the **receipt** in case you want a refund. — receipt 收据 n.
15. The shirt shrank, so I asked for a **refund**. — refund 退款 n.
16. This store offers a ten percent **discount** for students. — discount 折扣 n.
17. She **bargained** with the seller and saved twenty yuan. — bargain 讨价还价 v.
18. The **cashier** scanned my items quickly. — cashier 收银员 n.
19. Push the shopping **cart** slowly, please. — cart 购物车 n.
20. Bread is in **aisle** three. — aisle 过道 n.
21. There are too many people at the **checkout**. — checkout 收银台 n.
22. I cut out a **coupon** from the newspaper. — coupon 优惠券 n.
23. This **brand** of milk is my favorite. — brand 品牌 n.
24. The **quality** of these shoes is excellent. — quality 质量 n.
25. The shop **delivers** fresh fruit to your door. — deliver 配送 v.
26. Free **delivery** for orders over fifty yuan. — delivery 送货 n.
27. Living near a supermarket is very **convenient**. — convenient 方便的 adj.
28. Can I **exchange** this sweater for a bigger one? — exchange 换货 v.
29. I bought a **secondhand** bike for only 100 yuan. — secondhand 二手的 adj.
30. This **product** is made in Germany. — product 产品 n.
31. The **customer** is always right, they say. — customer 顾客 n.
32. I paid by **credit** card. — credit 信用 n.
33. He took out his **wallet** to pay. — wallet 钱包 n.
34. A shiny **coin** rolled under the table. — coin 硬币 n.
35. Dinner came to 120 yuan — let's split the **bill**. — bill 账单 n.
36. I **purchased** a new phone online. — purchase 购买 v.
37. Each **item** in this store is checked twice. — item 物品 n.
38. Sorry, that size is out of **stock**. — stock 库存 n.
39. Is this seat still **available**? — available 可用的 adj.
40. **Compare** the prices before you buy. — compare 比较 v.
41. Don't drink that milk — it's **expired**. — expire 过期 v.
42. She **squeezed** the lemon into the tea. — squeeze 挤 v.
43. Be careful, or you'll **spill** the soup. — spill 洒出 v.
44. **Wipe** the table with a wet cloth. — wipe 擦 v.
45. He **folded** the clothes and put them away. — fold 叠 v.
46. You need to **scrub** the pot — the rice is stuck. — scrub 用力擦洗 v.
47. He **polished** his shoes until they shone. — polish 擦亮 v.
48. Throw the **trash** into the bin, not on the floor. — trash 垃圾 n.
49. We **recycle** paper, glass and plastic at home. — recycle 回收 v.
50. Doing chores teaches children **independence**. — independence 独立 n.`

const unit3Raw = `1. Sorry, I can't come — I have to **attend** a meeting. — attend 出席 v.
2. The **deadline** for the report is Friday. — deadline 截止日期 n.
3. She works **overtime** three nights a week. — overtime 加班 adv./n.
4. My **colleagues** are friendly and helpful. — colleague 同事 n.
5. He was **promoted** to manager last month. — promote 晋升 v.
6. She applied for a **position** in a foreign company. — position 职位 n.
7. Send me your **résumé** and I'll forward it to the company. — résumé 简历 n.
8. I have a job **interview** tomorrow morning. — interview 面试 n.
9. His **salary** is enough for a small family. — salary 薪水 n.
10. Workers get a **bonus** at the end of the year. — bonus 奖金 n.
11. The company has over two hundred **staff**. — staff 全体员工 n.
12. New employees receive two weeks of **training**. — training 培训 n.
13. Check my **schedule** — am I free at three? — schedule 日程表 n.
14. I made an **appointment** with the dentist. — appointment 预约 n.
15. My first **task** today is to answer emails. — task 任务 n.
16. This **project** will take about two months. — project 项目 n.
17. The **employee** of the month gets a free lunch. — employee 雇员 n.
18. A good **employer** cares about workers' health. — employer 雇主 n.
19. Changing jobs was an important step in her **career**. — career 事业 n.
20. Morning exercise is part of my daily **routine**. — routine 日常惯例 n.
21. His job **application** was accepted. — application 申请 n.
22. It's noisy here — I can't **concentrate**. — concentrate 专心 v.
23. The **semester** ends in January. — semester 学期 n.
24. She won a **scholarship** to study in Beijing. — scholarship 奖学金 n.
25. The professor's **lecture** was interesting. — lecture 讲座 n.
26. A **professor** from Oxford will speak today. — professor 教授 n.
27. We did a chemistry **experiment** in class. — experiment 实验 n.
28. The **laboratory** is on the third floor. — laboratory 实验室 n.
29. I love **literature** more than math. — literature 文学 n.
30. Your **grammar** is good, but your spelling needs work. — grammar 语法 n.
31. Practice your **pronunciation** every morning. — pronunciation 发音 n.
32. The first **paragraph** of your essay is too long. — paragraph 段落 n.
33. Write an **essay** about your hometown. — essay 作文 n.
34. Make an **outline** before you write. — outline 提纲 n.
35. This is only the first **draft** of my speech. — draft 草稿 n.
36. **Revise** your composition and hand it in again. — revise 修改 v.
37. You must **memorize** these twenty words by Friday. — memorize 记忆 v.
38. She is doing **research** on sea animals. — research 研究 n.
39. The teacher collected our **assignments**. — assignment 作业 n.
40. My **tutor** helps me with math on weekends. — tutor 家教 n.
41. He received his **diploma** last June. — diploma 毕业文凭 n.
42. A university **degree** is important for this job. — degree 学位 n.
43. The **campus** is beautiful in autumn. — campus 校园 n.
44. We eat lunch in the school **canteen**. — canteen 食堂 n.
45. My brother lives in a school **dormitory**. — dormitory 宿舍 n.
46. You must **register** before September 1st. — register 注册 v.
47. Remember to **submit** your homework online. — submit 提交 v.
48. We had a surprise **quiz** in English class. — quiz 小测验 n.
49. Good schools need clear rules and **discipline**. — discipline 纪律 n.
50. Winning the game was a great **achievement**. — achievement 成就 n.`

const unit4Raw = `1. Her dream is to travel **abroad** next year. — abroad 在国外 adv.
2. Check that your **passport** is not out of date. — passport 护照 n.
3. You need a **visa** to visit that country. — visa 签证 n.
4. She **packed** her **suitcase** the night before. — pack 打包 v.; suitcase 行李箱 n.
5. The airline lost my **luggage**. — luggage 行李 n.
6. Our **flight** leaves at 8:30 tomorrow morning. — flight 航班 n.
7. Passengers should **board** the plane at gate five. — board 登机 v.
8. The train was **delayed** for two hours. — delay 延误 v.
9. The Beijing train leaves from **platform** nine. — platform 站台 n.
10. The bus **fare** went up again. — fare 车费 n.
11. A free **shuttle** bus takes guests to the airport. — shuttle 班车 n.
12. Don't drive during **rush hour** — the roads are full. — rush hour 高峰时段 n.
13. **Pedestrians** should cross at the traffic lights. — pedestrian 行人 n.
14. Walk on the **sidewalk**, not on the road. — sidewalk 人行道 n.
15. The **highway** was busy all weekend. — highway 高速公路 n.
16. Turn left at the next **intersection**. — intersection 十字路口 n.
17. Fasten your **seatbelt** before takeoff. — seatbelt 安全带 n.
18. He pressed the **brake** and the car stopped. — brake 刹车 n.
19. A truck was blocking our **lane**. — lane 车道 n.
20. We stopped to buy **fuel** on the way. — fuel 燃料 n.
21. The car's **engine** makes a strange noise. — engine 发动机 n.
22. One **tire** is flat — we need help. — tire 轮胎 n.
23. We stayed in a cheap **hostel** near the station. — hostel 青年旅舍 n.
24. I'd like to make a **reservation** for two nights. — reservation 预订 n.
25. Leave your key at the **reception** when you go out. — reception 前台 n.
26. I bought a small **souvenir** for my sister. — souvenir 纪念品 n.
27. The mountain **scenery** took my breath away. — scenery 风景 n.
28. The city is full of **tourists** in summer. — tourist 游客 n.
29. Sanya is a popular travel **destination**. — destination 目的地 n.
30. The Eiffel Tower is the most famous **landmark** in Paris. — landmark 地标 n.
31. We visited an old **temple** on the mountain. — temple 寺庙 n.
32. The art **gallery** is free on Mondays. — gallery 美术馆 n.
33. Our hotel is right on the **coast**. — coast 海岸 n.
34. The house stands on a **cliff** above the sea. — cliff 悬崖 n.
35. We hiked to a beautiful **waterfall**. — waterfall 瀑布 n.
36. Camels carry travelers across the **desert**. — desert 沙漠 n.
37. Monkeys jumped around in the **jungle**. — jungle 丛林 n.
38. The village lies in a green **valley**. — valley 山谷 n.
39. They explored a dark **cave** near the beach. — cave 洞穴 n.
40. A clear **stream** runs behind my grandma's house. — stream 小溪 n.
41. Drive slowly — the **fog** is thick this morning. — fog 雾 n.
42. The **thunder** frightened the little dog. — thunder 雷 n.
43. The sky flashed with **lightning**. — lightning 闪电 n.
44. The air is hot and **humid** in the south. — humid 潮湿的 adj.
45. The lake **freezes** in winter. — freeze 结冰 v.
46. The snow **melts** in March. — melt 融化 v.
47. We watched the **sunset** over the sea. — sunset 日落 n.
48. Children love to **explore** new places. — explore 探索 v.
49. At **customs**, the officer checked my bags. — customs 海关 n.
50. Camping in the mountains was a real **adventure**. — adventure 冒险 n.`

const unit5Raw = `1. I have a **sore throat** and a runny nose. — sore throat 嗓子痛 n.
2. A fever is a common **symptom** of the flu. — symptom 症状 n.
3. Cover your mouth when you **sneeze**. — sneeze 打喷嚏 v.
4. The **virus** spreads quickly in winter. — virus 病毒 n.
5. Wash your hands — **germs** are everywhere. — germ 细菌 n.
6. The nurse gave me an **injection** in the arm. — injection 注射 n.
7. Children get a **vaccine** before school starts. — vaccine 疫苗 n.
8. It took him a month to **recover** from the illness. — recover 恢复 v.
9. He **injured** his knee while playing basketball. — injure 使受伤 v.
10. The **wound** on my hand is almost healed. — wound 伤口 n.
11. Put a clean **bandage** on the cut. — bandage 绷带 n.
12. Call an **ambulance** — he can't move! — ambulance 救护车 n.
13. In an **emergency**, dial 120. — emergency 紧急情况 n.
14. The **pharmacy** is open until ten at night. — pharmacy 药店 n.
15. Take one **pill** after each meal. — pill 药片 n.
16. **Swallow** the medicine with warm water. — swallow 吞下 v.
17. I feel **dizzy** if I stand up too fast. — dizzy 头晕的 adj.
18. She **fainted** because of the heat. — faint 晕倒 v.
19. He has an **allergy** to pollen. — allergy 过敏 n.
20. Good **nutrition** is important for children. — nutrition 营养 n.
21. Eggs and fish are rich in **protein**. — protein 蛋白质 n.
22. Fresh fruit gives you **vitamins**. — vitamin 维生素 n.
23. Slow eating helps you **digest** food better. — digest 消化 v.
24. A walk before dinner gives me a good **appetite**. — appetite 食欲 n.
25. He is a little **overweight** and wants to exercise more. — overweight 超重的 adj.
26. She goes to the gym to improve her **fitness**. — fitness 健康状况 n.
27. **Stretch** your legs before you run. — stretch 伸展 v.
28. **Breathe** deeply and count to ten. — breathe 呼吸 v.
29. Smoking is bad for your **lungs**. — lung 肺 n.
30. Strong **muscles** protect your back. — muscle 肌肉 n.
31. The heart is the most important **organ** in the body. — organ 器官 n.
32. Exercise is good for your **mental** health. — mental 精神的 adj.
33. Too much stress can lead to **depression**. — depression 抑郁 n.
34. She felt great **anxiety** before the results came out. — anxiety 焦虑 n.
35. Too much **stress** at work made him sick. — stress 压力 n.
36. I get **tense** when people argue. — tense 紧张的 adj.
37. Don't **panic** — we still have time. — panic 恐慌 v.
38. He was **frustrated** because the computer crashed again. — frustrated 沮丧的 adj.
39. She was **jealous** of her friend's new bike. — jealous 嫉妒的 adj.
40. He felt **ashamed** of his rude words. — ashamed 羞愧的 adj.
41. I felt **guilty** about forgetting her birthday. — guilty 内疚的 adj.
42. The boy was **embarrassed** when he fell over. — embarrassed 尴尬的 adj.
43. Try to stay **optimistic** even when things go wrong. — optimistic 乐观的 adj.
44. Don't be so **pessimistic** — it might work! — pessimistic 悲观的 adj.
45. I'm **delighted** to hear your good news. — delighted 高兴的 adj.
46. She was **annoyed** by the loud noise next door. — annoy 使恼怒 v.
47. I'm really **grateful** for your help. — grateful 感激的 adj.
48. She showed great **sympathy** for the poor. — sympathy 同情 n.
49. Her kind words were a great **comfort** to me. — comfort 安慰 n.
50. He's in a good **mood** today. — mood 心情 n.`

const unit6Raw = `1. Thank you for your **invitation** to the party. — invitation 邀请 n.
2. She had to **decline** the invitation because she was busy. — decline 婉拒 v.
3. Our **host** cooked a wonderful dinner. — host 主人 n.
4. More than thirty **guests** came to the wedding. — guest 客人 n.
5. He is an old **acquaintance** from my school days. — acquaintance 熟人 n.
6. My dog is my closest **companion**. — companion 伙伴 n.
7. They sat in the kitchen, **gossiping** about their neighbors. — gossip 闲聊 v.
8. He **greeted** me with a warm smile. — greet 问候 v.
9. Grandma **hugged** everyone at the door. — hug 拥抱 v.
10. We said our **farewells** at the airport. — farewell 告别 n.
11. I must **apologize** for being so late. — apologize 道歉 v.
12. She found it hard to **forgive** him. — forgive 原谅 v.
13. The two boys **quarreled** over a toy. — quarrel 争吵 v.
14. A short talk solved the **conflict** between them. — conflict 冲突 n.
15. Don't **misunderstand** me — I'm only trying to help. — misunderstand 误解 v.
16. The two teams **cooperate** very well. — cooperate 合作 v.
17. He finds it hard to **socialize** with strangers. — socialize 社交 v.
18. We're having a family **gathering** this weekend. — gathering 聚会 n.
19. The wedding **ceremony** took place in a garden. — ceremony 仪式 n.
20. They celebrate their wedding **anniversary** every May. — anniversary 周年纪念日 n.
21. The festival dinner was a real **feast**. — feast 盛宴 n.
22. Everyone raised their glasses for a **toast**. — toast 敬酒 n.
23. We had a **barbecue** in the park on Sunday. — barbecue 烧烤 n.
24. Her new **album** comes out next month. — album 专辑 n.
25. I can't hear the **lyrics** clearly. — lyric 歌词 n.
26. This song has a strong, fast **rhythm**. — rhythm 节奏 n.
27. That old **melody** always makes me smile. — melody 旋律 n.
28. He plays the **drums** in a rock band. — drum 鼓 n.
29. Please speak into the **microphone**. — microphone 麦克风 n.
30. The **audience** clapped for five minutes. — audience 观众 n.
31. The dance **performance** was amazing. — performance 表演 n.
32. The actors walked onto the **stage**. — stage 舞台 n.
33. The famous **actress** grew up in this town. — actress 女演员 n.
34. The movie's opening **scene** is unforgettable. — scene 场景 n.
35. Can you follow the **plot** so far? — plot 情节 n.
36. I watch English movies with **subtitles**. — subtitle 字幕 n.
37. This **documentary** is about wild animals in Africa. — documentary 纪录片 n.
38. We laughed all the way through the **comedy**. — comedy 喜剧 n.
39. The **tragedy** ends with the hero's death. — tragedy 悲剧 n.
40. I don't like **horror** movies — they scare me. — horror 恐怖 n.
41. My little sister loves Japanese **animation**. — animation 动画 n.
42. I missed the first **episode** of the show. — episode 一集 n.
43. The game will be **broadcast** live tonight. — broadcast 播出 v.
44. They put up a **poster** for the school concert. — poster 海报 n.
45. Reading is her favorite **leisure** activity. — leisure 休闲 n.
46. The city offers many kinds of **entertainment**. — entertainment 娱乐 n.
47. The kids screamed with joy on the **roller coaster**. — roller coaster 过山车 n.
48. Chess is my favorite **board game**. — board game 棋类游戏 n.
49. The children guessed the answer to the **riddle**. — riddle 谜语 n.
50. The **magician** performed amazing tricks. — magician 魔术师 n.`

export const sentenceGroupMap: Record<string, SentenceGroup> = {
  'a1-l1-u1': parseGroup('a1-l1-u1-sentences', 'Personal Life', '个人生活 · 50 句', unit1Raw),
  'a1-l1-u2': parseGroup(
    'a1-l1-u2-sentences',
    'Daily Routine & Shopping',
    '日常生活与购物 · 50 句',
    unit2Raw,
  ),
  'a1-l1-u3': parseGroup('a1-l1-u3-sentences', 'Work & Study', '工作与学习 · 50 句', unit3Raw),
  'a1-l1-u4': parseGroup(
    'a1-l1-u4-sentences',
    'Travel & Transport',
    '旅行与交通 · 51 句',
    unit4Raw,
  ),
  'a1-l1-u5': parseGroup(
    'a1-l1-u5-sentences',
    'Health & Feelings',
    '健康与情绪 · 50 句',
    unit5Raw,
  ),
  'a1-l1-u6': parseGroup(
    'a1-l1-u6-sentences',
    'Social & Entertainment',
    '社交与娱乐 · 50 句',
    unit6Raw,
  ),
}
