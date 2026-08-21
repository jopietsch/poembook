# -*- coding: utf-8 -*-
"""
Data for "Poems to Cherish and Memorize".

Each poem is a dict:
    num        display number ("§0" for a seed work, otherwise numeric)
    title      poem title
    author     author name
    dates      publication / composition note
    form       form and length note
    why        the commentary
    difficulty memorization difficulty
    links      list of (label, url)
    pd         True if public domain in the US
    ws         Wikisource search string (only meaningful if pd), or None
    flag       optional warning string (for poems with no free authorized text)
"""

CATEGORIES = [
    {
        "id": "a",
        "title": "The Hound of Heaven line",
        "subtitle": "Pursuit, flight, wrestling with God, the long breath",
        "intro": (
            "Thompson's poem is late-Victorian and a bit overstuffed, but its engine "
            "\u2014 <em>being chased by a love you're fleeing</em> \u2014 has a deep tradition "
            "behind it. Most poems in this thread are in the public domain in the US; "
            "full texts are included where rights permit."
        ),
    },
    {
        "id": "b",
        "title": "The Kindness line",
        "subtitle": "Contemporary, plainspoken, sorrow turned toward mercy",
        "intro": (
            "<strong>All poems in this thread are under active copyright</strong>, so no texts appear here \u2014 "
            "only links to authorized sources where the publisher has granted permission. "
            "Please read them there rather than on scraper sites; poets.org and the Poetry "
            "Foundation are part of how living poets get paid."
        ),
    },
    {
        "id": "c",
        "title": "The \u201cHope is the thing with feathers\u201d line",
        "subtitle": "Compact, metrical, one image carried all the way",
        "intro": (
            "The most memorizable category by a wide margin, and entirely public domain. "
            "If you want fast wins, start here."
        ),
    },
    {
        "id": "d",
        "title": "The Rilke line",
        "subtitle": "Solitude, attention, terror, and the demand to be transformed",
        "intro": (
            "Rilke makes a fourth path through the book: the world looks back at us, "
            "beauty is inseparable from terror, and sustained attention becomes a demand "
            "to change. The included English texts use Jessie Lemont's public-domain 1918 "
            "translations. Modern translations are linked when their choices are important."
        ),
    },
    {
        "id": "e",
        "title": "The Saint Patrick's Breastplate line",
        "subtitle": "Protection, courage, the world made into prayer",
        "intro": (
            "A <em>lorica</em> is a prayer worn as armor. This thread begins with the "
            "great Irish hymn traditionally attributed to Patrick: its protection is not "
            "withdrawal from the world, but Christ before, behind, beneath, above, and "
            "within the speaker. Its contemporary companion poems remain linked rather than "
            "reprinted, so their authors and publishers can be supported."
        ),
    },
    {
        "id": "f",
        "title": "The Canticle of the Sun line",
        "subtitle": "Creaturely kinship, praise, poverty, and a companionable death",
        "intro": (
            "Francis calls sun, moon, wind, water, fire, earth, and even bodily death "
            "brother or sister. This is praise that does not leave the material world "
            "behind: it learns to receive creation as family. Its contemporary companion poems "
            "remain linked rather than reprinted, so their authors and publishers can be supported."
        ),
    },
]

DICKINSON_NOTE = (
    "<p><strong>A note on Dickinson texts.</strong> Use the <strong>Franklin</strong> numbering (Fr) and the "
    "R. W. Franklin <em>Reading Edition</em> (1999), the Emily Dickinson Archive "
    "(edickinson.org), or the Poetry Foundation links below \u2014 which use Franklin numbers "
    "and restore her punctuation. Nineteenth- and early-twentieth-century editors "
    "\u201ccorrected\u201d her dashes, capitals, and rhymes; a complete restored edition didn't "
    "appear until Franklin's in 1998, and many free sites still carry the bowdlerized "
    "texts. Her poems are in <strong>hymn meter</strong> (common metre, 8-6-8-6), which is why they're "
    "so memorizable: nearly every one can be sung to \u201cAmazing Grace.\u201d Use that. It's not "
    "a gimmick; it's how the poems are built.</p>"
)

POEMS = {
"a": [
    dict(num="\u00a70", seed=True,
         title="The Hound of Heaven", author="Francis Thompson",
         dates="first printed July 1890 in <em>Merry England</em>; coll. <em>Poems</em>, 1893",
         form="182 lines, irregular ode",
         why="Your seed. The soul flees down the nights and down the days, down the "
             "labyrinthine ways of its own mind, and the pursuit never hurries and never "
             "stops. Included in the <em>Oxford Book of English Mystical Verse</em> (1917), which "
             "is largely how it reached the audience it has. Worth knowing that Eugene "
             "O'Neill could recite the whole thing from memory, which is either encouraging "
             "or daunting depending on the day. Most people who \u201cknow\u201d it know the opening "
             "verse paragraph and the closing dozen lines; that is a legitimate way to hold it.",
         difficulty="Hard \u2014 by a wide margin the longest and most difficult poem here, and the "
                    "irregular metre gives you far less scaffolding than its Victorian surface suggests",
         memory_map=["The flight begins", "Creation refuses refuge", "Human loves fail",
                     "Childhood, nature, and time", "The pursuer confronts the soul",
                     "The final answer"],
         links=[("Project Gutenberg (1922 ed., with notes)",
                 "https://www.gutenberg.org/files/30730/30730-h/30730-h.htm")],
         pd=True, ws="The Hound of Heaven Francis Thompson"),

    dict(num="1", title="Love (III)", author="George Herbert",
         dates="1633, <em>The Temple</em>", form="18 lines, three sestets, rhymed",
         why="The single best companion to your Thompson: this is the flight <em>ended</em>. The soul "
             "draws back out of shame, and Love simply keeps insisting until it sits down and "
             "eats. Simone Weil recited this as a prayer during migraine attacks. If you "
             "memorize one poem from this category, this one.",
         difficulty="Easy",
         memory_map=["Love welcomes; the soul withdraws", "The guest feels unworthy",
                     "Love bears the blame and serves the meal"],
         links=[("poets.org", "https://poets.org/poem/love-iii"),
                ("Poetry Foundation (annotated)", "https://www.poetryfoundation.org/poems/44367/love-iii")],
         pd=True, ws="Love III George Herbert The Temple"),

    dict(num="2", title="The Collar", author="George Herbert",
         dates="1633, <em>The Temple</em>", form="36 lines",
         why="The other half: this is the flight itself. A tantrum against God, mounting for "
             "32 lines, broken by one word in the last four. The line lengths are deliberately "
             "ragged \u2014 the form is falling apart because the speaker is. Note the structural "
             "joke: the rhyme scheme closes where it opened, so the poem is itself a collar.",
         difficulty="Moderate",
         links=[("poets.org", "https://poets.org/poem/collar"),
                ("Poetry Foundation", "https://www.poetryfoundation.org/poems/44360/the-collar")],
         pd=True, ws="The Collar George Herbert"),

    dict(num="3", title="The Pulley", author="George Herbert",
         dates="1633, <em>The Temple</em>", form="20 lines",
         why="God pours every blessing into man but withholds rest, so that weariness may toss "
             "him back. The conceit of your Thompson in miniature: restlessness as the "
             "<em>mechanism</em> of return.",
         difficulty="Easy",
         links=[("poets.org author page", "https://poets.org/poet/george-herbert")],
         pd=True, ws="The Pulley George Herbert"),

    dict(num="4", title="Batter my heart, three-person'd God", author="John Donne",
         dates="Holy Sonnet XIV, pub. 1633", form="14 lines, sonnet",
         why="Divine pursuit at its most violent and frankly erotic \u2014 the speaker asks to be "
             "besieged, imprisoned, ravished. Nothing in Thompson is this compressed or this "
             "shocking. Oppenheimer named the Trinity test after it.",
         difficulty="Easy as a sonnet; the syntax fights you",
         links=[("poets.org", "https://poets.org/poem/batter-my-heart-three-persond-god-holy-sonnet-14")],
         pd=True, ws="Holy Sonnets Batter my heart John Donne"),

    dict(num="5", title="God's Grandeur", author="Gerard Manley Hopkins",
         dates="1877, pub. 1918", form="14 lines, sonnet",
         why="Start Hopkins here. Sprung rhythm hits the ear the way Thompson's anapests do but "
             "denser, stranger, better. The world is charged, and despite everything the Holy "
             "Ghost broods over it with warm breast and bright wings.",
         difficulty="Easy\u2013Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44395/gods-grandeur"),
                ("Audio", "https://www.poetryfoundation.org/audio/76201/gods-grandeur")],
         pd=True, ws="God's Grandeur Gerard Manley Hopkins"),

    dict(num="6", title="The Windhover", author="Gerard Manley Hopkins",
         dates="1877, pub. 1918", form="14 lines, sonnet, dedicated \u201cTo Christ our Lord\u201d",
         why="A kestrel in flight becomes the sight of Christ. Hopkins called it the best thing "
             "he ever wrote. Extraordinary out loud.",
         difficulty="Moderate \u2014 the compound coinages are hard to hold",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44402/the-windhover")],
         pd=True, ws="The Windhover Gerard Manley Hopkins"),

    dict(num="7", title="Carrion Comfort", author="Gerard Manley Hopkins",
         dates="1885, pub. 1918", form="14 lines, sonnet",
         why="The first of the \u201cterrible sonnets.\u201d Wrestling with God as literal wrestling \u2014 and "
             "at the end, the horror of realizing who the opponent was. This is Thompson's "
             "territory taken seriously. Save it until you've done two easier Hopkins.",
         difficulty="Moderate\u2013Hard",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44392/carrion-comfort"),
                ("Audio", "https://www.poetryfoundation.org/audio/76200/carrion-comfort")],
         pd=True, ws="Carrion Comfort Gerard Manley Hopkins"),

    dict(num="8", title="Thou art indeed just, Lord, if I contend", author="Gerard Manley Hopkins",
         dates="1889, pub. 1918", form="14 lines, sonnet, with a Latin epigraph from Jeremiah",
         why="The complaint poem: <em>why do sinners' ways prosper.</em> Ends asking God to send rain "
             "to his roots. Written months before his death.",
         difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44404/thou-art-indeed-just-lord-if-i-contend")],
         pd=True, ws="Thou art indeed just Lord Hopkins"),

    dict(num="9", title="Up-Hill", author="Christina Rossetti",
         dates="written 1858, pub. 1862 in <em>Goblin Market and Other Poems</em>",
         form="16 lines, question-and-answer",
         why="A traveler asks whether the road winds uphill all the way; an unnamed voice "
             "answers. Deceptively plain, and it lodges permanently. One of the easiest here \u2014 "
             "the dialogue structure does half the work.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/hill")],
         pd=True, ws="Up-Hill Christina Rossetti"),

    dict(num="10", title="When I Consider How My Light Is Spent", author="John Milton",
         dates="Sonnet 19, comp. c. 1652\u201355, pub. 1673", form="14 lines, sonnet",
         why="Milton going blind, asking whether God exacts day-labour from a man denied light \u2014 "
             "and being answered by Patience. Ends on one of the most famous lines in English. "
             "Note: the familiar title \u201cOn His Blindness\u201d is not Milton's; an editor added it in 1761.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/when-i-consider-how-my-light-spent"),
                ("Poetry Foundation", "https://www.poetryfoundation.org/poems/44750/sonnet-19-when-i-consider-how-my-light-is-spent")],
         pd=True, ws="When I consider how my light is spent Milton sonnet"),

    dict(num="11", title="They Are All Gone into the World of Light", author="Henry Vaughan",
         dates="1655, <em>Silex Scintillans</em>", form="40 lines, quatrains",
         why="Vaughan is the underrated one in this company. Grief and longing for the dead "
             "turned into a metaphysics of light. Quatrains make it far easier than the length suggests.",
         difficulty="Moderate",
         links=[("Poetry Archive", "https://poetryarchive.org/poem/they-are-all-gone-into-world-light/")],
         pd=True, ws="They are all gone into the world of light Vaughan"),

    dict(num="12", title="Journey of the Magi", author="T. S. Eliot",
         dates="1927, <em>Ariel Poems</em>", form="43 lines, free verse",
         why="The <em>cost</em> of being found. Conversational surface \u2014 a tired old man remembering a "
             "hard trip \u2014 with devastation underneath. Public domain in the US as of 2023, but "
             "note that Eliot died in 1965, so this is still in copyright in the UK and EU until 2036.",
         difficulty="Moderate\u2013Hard",
         links=[("poets.org", "https://poets.org/poem/journey-magi"),
                ("Eliot reading it himself \u2014 Poetry Archive", "https://poetryarchive.org/poem/journey-magi/")],
         pd=True, ws="Journey of the Magi T. S. Eliot",
         extract_after="JOURNEY OF THE MAGI"),
],

"b": [
    dict(num="\u00a70", seed=True,
         title="Kindness", author="Naomi Shihab Nye",
         dates="coll. <em>Words Under the Words: Selected Poems</em>, Far Corner Books, 1995",
         form="free verse, ~40 lines",
         why="Your seed. Before you know what kindness really is you must lose things; before "
             "you know kindness as the deepest thing inside, you must know sorrow as the other "
             "deepest thing. Nye has said it came out of being robbed of everything on her "
             "honeymoon in South America and the kindness of a stranger afterward. Note how the "
             "poem refuses to arrive at comfort until it has fully paid for it; that refusal is "
             "what the rest of this category has in common.",
         difficulty="Moderate\u2013Hard \u2014 long for free verse, but the two-part argument "
                    "(first you must lose, <em>then</em> you must grieve) is the spine to learn it by",
         links=[("poets.org", "https://poets.org/poem/kindness")],
         pd=False, ws=None),

    dict(num="1", title="Love After Love", author="Derek Walcott",
         dates="1976, <em>Sea Grapes</em>; coll. <em>Collected Poems 1948\u20131984</em>",
         form="15 lines, free verse",
         why="The stranger who has loved you all your life turns out to be you. Give wine, give "
             "bread, sit, feast on your life.",
         difficulty="Moderate \u2014 free verse, but the logic (arrival \u2192 recognition \u2192 feast) carries it",
         links=[("poets.org", "https://poets.org/poem/love-after-love")], pd=False, ws=None),

    dict(num="2", title="The Thing Is", author="Ellen Bass",
         dates="2002, <em>Mules of Love</em>, BOA Editions", form="free verse, ~20 lines",
         why="How to love life again when grief has made it physically unbearable \u2014 grief as "
             "tropical heat, as an obesity you carry. Ends by holding life like a plain face and "
             "saying yes anyway. The closest sibling to your Nye of anything on this list.",
         difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/151844/the-thing-is")],
         pd=False, ws=None),

    dict(num="3", title="A Brief for the Defense", author="Jack Gilbert",
         dates="2005, <em>Refusing Heaven</em>, Knopf", form="~30 lines, free verse",
         why="An argument that we are <em>obligated</em> to be joyful in a world of atrocity \u2014 that "
             "refusing delight doesn't honor the suffering, it insults it. Fierce and completely "
             "unsentimental.",
         difficulty="Hard \u2014 the longest here, but the argument structure helps",
         links=[("Poetry Society of America", "https://poetrysociety.org/poems/a-brief-for-the-defense")],
         pd=False, ws=None),

    dict(num="4", title="blessing the boats", author="Lucille Clifton",
         dates="1991, <em>Collected Poems</em>, BOA Editions", form="13 lines, lowercase, no punctuation",
         why="A benediction for someone setting out: may the tide carry you out beyond the face "
             "of fear. Reads aloud like a blessing because it is one. One of the easiest poems "
             "on this entire list.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/blessing-boats")], pd=False, ws=None),

    dict(num="5", title="won't you celebrate with me", author="Lucille Clifton",
         dates="1991, <em>Collected Poems</em>, BOA Editions", form="15 lines",
         why="Survival as celebration \u2014 born in babylon, both nonwhite and woman, with no model, "
             "and every day something has tried to kill her and failed. It answers Whitman's "
             "\u201cI celebrate myself\u201d from a position Whitman never occupied. Clifton said she "
             "wrote it on a day a colleague had hurt her feelings.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/wont-you-celebrate-me")], pd=False, ws=None),

    dict(num="6", title="The Peace of Wild Things", author="Wendell Berry",
         dates="1968, <em>Openings</em>; coll. <em>Collected Poems</em>, 1985", form="11 lines, free verse",
         why="Waking in the night in fear for your children's lives, and going to lie down where "
             "the wood drake rests. The day-blind stars waiting with their light.",
         difficulty="Easy",
         links=[("On Being", "https://onbeing.org/poetry/the-peace-of-wild-things/"),
                ("Scottish Poetry Library", "https://www.scottishpoetrylibrary.org.uk/poem/peace-wild-things-0/")],
         pd=False, ws=None),

    dict(num="7", title="In Blackwater Woods", author="Mary Oliver",
         dates="1983, <em>American Primitive</em>", form="free verse, 9 stanzas",
         why="You probably know \u201cWild Geese.\u201d This is the deeper one: to live in this world you "
             "must love what is mortal, hold it against your bones, and \u2014 when the time comes \u2014 "
             "let it go.",
         difficulty="Moderate",
         flag="No authorized free full text. Oliver's estate licenses very restrictively and she "
              "is largely absent from poets.org and the Poetry Foundation. Buy <em>American Primitive</em> "
              "(Back Bay Books) or <em>Devotions</em> (Penguin, 2017), which collects it.",
         links=[], pd=False, ws=None),

    dict(num="8", title="What the Living Do", author="Marie Howe",
         dates="1997, <em>What the Living Do</em>, Norton", form="free verse",
         why="Addressed to her brother John, dead of an AIDS-related illness. Grief inside "
             "ordinary domestic mess \u2014 a clogged drain, spilled coffee, wanting more and more and "
             "then more of it. Ends with a shock of self-recognition in a shop window. Took her "
             "eight years to write.",
         difficulty="Moderate\u2013Hard",
         links=[("poets.org", "https://poets.org/poem/what-living-do")], pd=False, ws=None),

    dict(num="9", title="Try to Praise the Mutilated World", author="Adam Zagajewski, trans. Clare Cavanagh",
         dates="pub. <em>The New Yorker</em>, Sept. 2001; coll. <em>Without End</em>, FSG, 2002",
         form="21 lines",
         why="The \u201cyes, and still\u201d poem. Worth knowing: <strong>it was written well before 9/11</strong> \u2014 it "
             "came from Zagajewski traveling with his father through Polish villages emptied by "
             "post-Yalta population transfers, going to nettles and wild apple trees. It became "
             "the 9/11 poem by accident. The imperative escalates across the poem \u2014 <em>try to "
             "praise</em>, <em>you must praise</em>, <em>you should praise</em>, then simply <em>praise</em>. Learn it by "
             "that escalation.",
         difficulty="Moderate",
         flag="No authorized free full text found. It sits behind The New Yorker's archive; the "
              "widely circulated copies are unlicensed. Buy <em>Without End: New and Selected Poems</em> (FSG).",
         links=[], pd=False, ws=None),

    dict(num="10", title="Saint Francis and the Sow", author="Galway Kinnell",
         dates="1980, <em>Mortal Acts, Mortal Words</em>", form="free verse",
         why="Sometimes it is necessary to reteach a thing its loveliness \u2014 and Francis does it by "
             "putting his hand on a sow's brow and blessing her down the whole length of her "
             "body. Self-blessing made physical and unglamorous. A perfect companion to Walcott.",
         difficulty="Moderate",
         links=[("poets.org", "https://poets.org/poem/saint-francis-and-sow")], pd=False, ws=None),

    dict(num="11", title="Small Kindnesses", author="Danusha Lam\u00e9ris",
         dates="2020, <em>Bonfire Opera</em>, Univ. of Pittsburgh Press", form="free verse, short",
         why="A literal descendant of your Nye poem \u2014 Lam\u00e9ris followed Ellen Bass as Poet "
             "Laureate of Santa Cruz County. Strangers saying bless you when you sneeze (a "
             "leftover from the plague \u2014 <em>don't die</em>, we are saying), making room in the aisle, "
             "helping you pick up spilled lemons. The fleeting temples we build together.",
         difficulty="Easy\u2013Moderate",
         links=[("poets.org", "https://poets.org/poem/small-kindnesses")], pd=False, ws=None),

    dict(num="12", title="Famous", author="Naomi Shihab Nye",
         dates="1982, <em>Hugging the Jukebox</em>; coll. <em>Words Under the Words</em>, 1995",
         form="free verse, short",
         why="The river is famous to the fish; the boot is famous to the earth. Redefines fame as "
             "being useful to something specific. A federal appeals judge once quoted it in full "
             "in a concurring opinion.",
         difficulty="Easy\u2013Moderate",
         links=[("poets.org", "https://poets.org/poem/famous"),
                ("Poetry Foundation", "https://www.poetryfoundation.org/poems/47993/famous")],
         pd=False, ws=None),
],

"c": [
    dict(num="\u00a70", seed=True,
         title="\u201cHope\u201d is the thing with feathers", author="Emily Dickinson",
         dates="Fr314, c. 1862", form="12 lines, three quatrains, common metre",
         why="Your seed. The definition poem in its purest form: an abstraction pinned to one "
             "image and carried the whole distance without a slip. Hope perches in the soul, "
             "sings without words, never stops \u2014 and in the last stanza, in the chillest land and "
             "on the strangest sea, it never asked a crumb of the speaker. That final turn is "
             "the whole poem. Sings to \u201cAmazing Grace,\u201d like most of her.",
         difficulty="Easy",
         memory_map=["Hope becomes a bird", "The song persists through storms",
                     "It asks nothing in return"],
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/42889/hope-is-the-thing-with-feathers-314")],
         pd=True, ws="Hope is the thing with feathers Dickinson"),

    dict(num="1", title="Tell all the truth but tell it slant \u2014", author="Emily Dickinson",
         dates="Fr1263, c. 1872", form="8 lines",
         why="Truth's superb surprise must dazzle gradually or every man be blind. An ars "
             "poetica in eight lines.",
         difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/56824/tell-all-the-truth-but-tell-it-slant-1263")],
         pd=True, ws="Tell all the truth but tell it slant Dickinson"),

    dict(num="2", title="There's a certain Slant of light", author="Emily Dickinson",
         dates="Fr320, c. 1862", form="16 lines",
         why="Winter afternoons, cathedral tunes, heavenly hurt that leaves no scar. The single "
             "best thing ever written about seasonal despair. Yvor Winters ranked it among her "
             "three finest.",
         difficulty="Easy\u2013Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/45723/theres-a-certain-slant-of-light-320")],
         pd=True, ws="There's a certain slant of light Dickinson"),

    dict(num="3", title="After great pain, a formal feeling comes \u2014", author="Emily Dickinson",
         dates="Fr372, c. 1862", form="13 lines",
         why="The anaesthesia after grief \u2014 the hour of lead, the freezing persons recollecting "
             "the snow. Not in strict common metre, which makes it slightly harder.",
         difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/47651/after-great-pain-a-formal-feeling-comes-372")],
         pd=True, ws="After great pain a formal feeling comes Dickinson"),

    dict(num="4", title="I'm Nobody! Who are you?", author="Emily Dickinson",
         dates="Fr260, c. 1861", form="8 lines",
         why="Funny, which people forget she often is. How dreary to be somebody, like a frog "
             "telling your name to an admiring bog. The easiest Dickinson to memorize, full stop.",
         difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/1647321/im-nobody-who-are-you")],
         pd=True, ws="I'm nobody who are you Dickinson"),

    dict(num="5", title="Because I could not stop for Death \u2014", author="Emily Dickinson",
         dates="Fr479, c. 1862", form="24 lines, six quatrains",
         why="The carriage ride. Probably her greatest poem, and the narrative sequence (school, "
             "fields, setting sun, house in the ground) makes the length manageable.",
         difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/47652/because-i-could-not-stop-for-death-479"),
                ("Audio", "https://www.poetryfoundation.org/audio/76779/because-i-could-not-stop-for-death-479")],
         pd=True, ws="Because I could not stop for Death Dickinson"),

    dict(num="6", title="The Darkling Thrush", author="Thomas Hardy",
         dates="written Dec. 1900; pub. <em>Poems of the Past and the Present</em>, 1901", form="32 lines",
         why="<strong>The direct dark twin of your Dickinson seed, and the best single addition on this "
             "list.</strong> An aged thrush flings its soul upon the growing gloom at the turn of the "
             "century, and Hardy \u2014 who can see no reason whatever for hope \u2014 concludes the bird "
             "must know some blessed hope he doesn't. Where Dickinson's hope sings without asking "
             "anything, Hardy's sings against all evidence and baffles the listener. Read them "
             "back to back.",
         difficulty="Moderate",
         links=[("poets.org", "https://poets.org/poem/darkling-thrush"),
                ("Scottish Poetry Library", "https://www.scottishpoetrylibrary.org.uk/poem/darkling-thrush/")],
         pd=True, ws="The Darkling Thrush Thomas Hardy"),

    dict(num="7", title="Spring and Fall: to a young child", author="Gerard Manley Hopkins",
         dates="1880, pub. 1918", form="15 lines",
         why="Margaret is grieving over falling leaves; the speaker tells her that as she ages "
             "she'll grieve less for leaves and more for herself. One of the most perfect short "
             "poems in English.",
         difficulty="Easy\u2013Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44400/spring-and-fall")],
         pd=True, ws="Spring and Fall to a young child Hopkins"),

    dict(num="8", title="Remember", author="Christina Rossetti",
         dates="written 1849, pub. 1862", form="14 lines, sonnet",
         why="Remember me when I am gone away \u2014 and then the turn: better to forget and smile "
             "than remember and be sad. A sonnet that gives permission to be forgotten.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/remember")],
         pd=True, ws="Remember Christina Rossetti sonnet"),

    dict(num="9", title="The Lake Isle of Innisfree", author="W. B. Yeats",
         dates="written 1888, first pub. 1890", form="12 lines, three quatrains",
         why="Nine bean rows, a hive for the honeybee, peace dropping slow. Pure sound \u2014 you'll "
             "have it by heart before you've consciously tried. Yeats said it came from a sudden "
             "memory of childhood while walking down Fleet Street in London. It's printed in "
             "Irish passports.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/lake-isle-innisfree"),
                ("Poetry Foundation", "https://www.poetryfoundation.org/poems/43281/the-lake-isle-of-innisfree")],
         pd=True, ws="The Lake Isle of Innisfree Yeats"),

    dict(num="10", title="Loveliest of trees, the cherry now", author="A. E. Housman",
         dates="<em>A Shropshire Lad</em> II, 1896", form="12 lines, rhymed couplets",
         why="Fifty springs are little room, so he goes about the woodlands to see the cherry "
             "hung with snow. Housman's whole method \u2014 plainest words, exact metre, devastating "
             "arithmetic.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/loveliest-trees")],
         pd=True, ws="A Shropshire Lad Loveliest of trees Housman"),

    dict(num="11", title="Nothing Gold Can Stay", author="Robert Frost",
         dates="<em>The Yale Review</em>, Oct. 1923; coll. <em>New Hampshire</em>, 1923",
         form="8 lines, iambic trimeter, AABBCCDD",
         why="Nature's first green is gold. Dawn goes down to day. Eight lines and the argument "
             "is airtight. Entered US public domain in 2019 \u2014 but Frost died in 1963, so it "
             "remains in copyright in the UK and EU until 2034.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/nothing-gold-can-stay"),
                ("Poetry Foundation", "https://www.poetryfoundation.org/poems/148652/nothing-gold-can-stay-5c095cc5ab679")],
         pd=True, ws="Nothing Gold Can Stay Robert Frost"),

    dict(num="12", title="There Will Come Soft Rains", author="Sara Teasdale",
         dates="<em>Harper's</em>, July 1918; revised with the subtitle \u201cWar Time\u201d in <em>Flame and Shadow</em>, 1920",
         form="12 lines, rhymed couplets",
         why="Written during the German Spring Offensive and the influenza pandemic: nature will "
             "not notice or care when humanity is gone. Cool, level, pitiless.",
         difficulty="Easy",
         links=[("poets.org", "https://poets.org/poem/there-will-come-soft-rains")],
         pd=True, ws="There Will Come Soft Rains Teasdale"),
],
"e": [
    dict(num="§0", seed=True, title="Saint Patrick's Breastplate", author="Anonymous (traditionally Saint Patrick)",
         dates="Old Irish hymn; traditionally associated with Saint Patrick (5th century)",
         form="metrical translation, 11 stanzas",
         why="A prayer of encircling: Trinity, Christ's life, the communion of saints, and the "
             "created world become protection for a journey through danger. The recurring "
             "\u201cI bind unto myself to-day\u201d gives it a powerful memorization spine.",
         difficulty="Moderate \u2014 long, but carried by anaphora and hymn rhythm",
         memory_map=["Invocation of the Trinity", "Christ's life and return", "The communion of saints",
                     "The powers of creation", "God's guarding power", "Christ in every encounter", "Closing confession"],
         links=[("Wikisource: Cecil Frances Alexander translation", "https://en.wikisource.org/wiki/I_bind_unto_myself_to-day")],
         pd=True, ws="I bind unto myself to-day"),
    dict(num="1", title="A Blessing", author="James Wright", dates="1963", form="free verse",
         why="Two horses at the edge of a field make an ordinary walk into an encounter with a power that loosens the self. A breastplate need not harden us.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=A%20Blessing%20James%20Wright")], pd=False, ws=None),
    dict(num="2", title="The Waking", author="Theodore Roethke", dates="1953", form="villanelle",
         why="A disciplined answer to fear: wake into the life that is given, and learn by going where one has to go.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/58708/the-waking")], pd=False, ws=None),
    dict(num="3", title="The Peace of Wild Things", author="Wendell Berry", dates="1968", form="free verse",
         why="Fear is met not by denial but by putting the body among creatures that do not rehearse their own destruction.",
         difficulty="Easy\u2013Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Peace%20of%20Wild%20Things%20Wendell%20Berry")], pd=False, ws=None),
    dict(num="4", title="The Journey", author="Mary Oliver", dates="1986", form="free verse",
         why="The moment of leaving a chorus of bad advice behind: a companion to Patrick's clear, repeated choice to bind oneself to what saves.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Journey%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="5", title="When Death Comes", author="Mary Oliver", dates="1992", form="free verse",
         why="A fearless rehearsal for mortality that refuses both abstraction and panic; it belongs beside the breastplate's protection for the whole journey.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=When%20Death%20Comes%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="6", title="The Uses of Sorrow", author="Mary Oliver", dates="2007", form="short free verse",
         why="Sorrow is given a voice and refuses to be banished. Protection here means learning what may accompany us without ruling us.",
         difficulty="Easy", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Uses%20of%20Sorrow%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="7", title="A Ritual to Read to Each Other", author="William Stafford", dates="1976", form="free verse",
         why="Its watchfulness is communal rather than solitary: notice the signals, resist the simplifications, and keep each other from becoming lost.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=A%20Ritual%20to%20Read%20to%20Each%20Other%20William%20Stafford")], pd=False, ws=None),
    dict(num="8", title="To Be of Use", author="Marge Piercy", dates="1973", form="free verse",
         why="A praise poem for people who pull like water buffalo and do the work that must be done: courage made practical.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=To%20Be%20of%20Use%20Marge%20Piercy")], pd=False, ws=None),
    dict(num="9", title="Prayer", author="Carol Ann Duffy", dates="2005", form="four sestets, free verse",
         why="Grace arrives in secular sound: a train, a radio, the ordinary syllables that carry a person through an unchosen hour.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=Prayer%20Carol%20Ann%20Duffy")], pd=False, ws=None),
    dict(num="10", title="The Gift", author="Li-Young Lee", dates="1990", form="free verse",
         why="A father's care for a splinter becomes an inheritance of tenderness. It is a small, bodily form of the guarding love Patrick invokes.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Gift%20Li-Young%20Lee")], pd=False, ws=None),
    dict(num="11", title="Instructions on Not Giving Up", author="Ada Lim\u00f3n", dates="2017", form="free verse",
         why="After winter, a tree opens a new leaf anyway. The poem's stubborn, unshowy courage is a modern answer to the breastplate's daily resolve.",
         difficulty="Moderate", links=[("Academy of American Poets", "https://poets.org/poem/instructions-not-giving")], pd=False, ws=None),
],
"f": [
    dict(num="§0", seed=True, title="The Canticle of the Sun", author="Saint Francis of Assisi",
         dates="c. 1225; English translation in <em>The Writings of St. Francis of Assisi</em> (1906)",
         form="10 stanzas, free-verse translation",
         why="The elemental praise poem: sun and moon, wind and water, fire and earth are not "
             "scenery but kin. Its final turn to forgiveness, suffering, and \u201csister bodily death\u201d "
             "makes the joy durable rather than merely pastoral.",
         difficulty="Easy\u2013Moderate \u2014 short stanzas, repeated praise, and a clear procession through creation",
         memory_map=["Praise belongs to God", "Brother sun", "Sister moon and stars", "Wind and weather",
                     "Water and fire", "Mother earth", "Forgiveness and endurance", "Sister bodily death", "Final humility"],
         links=[("Wikisource: 1906 literal English translation", "https://en.wikisource.org/wiki/The_Writings_of_St._Francis_of_Assisi/The_Canticle_of_the_Sun")],
         pd=True, ws="The Writings of St Francis of Assisi The Canticle of the Sun"),
    dict(num="1", title="The Summer Day", author="Mary Oliver", dates="1990", form="free verse",
         why="A grasshopper becomes a teacher of attention, and attention becomes the question of what to do with one's one wild and precious life.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Summer%20Day%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="2", title="Sleeping in the Forest", author="Mary Oliver", dates="1979", form="free verse",
         why="The self lies down among the dark trees and wakes remade into something of their world: Francis's creaturely kinship turned inward.",
         difficulty="Easy\u2013Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=Sleeping%20in%20the%20Forest%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="3", title="The Wild Iris", author="Louise Gl\u00fcck", dates="1992", form="free verse",
         why="A flower speaks across death and return. It complicates Franciscan praise by letting creation answer back in a voice that is neither decorative nor tame.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Wild%20Iris%20Louise%20Gluck")], pd=False, ws=None),
    dict(num="4", title="The Trees", author="Philip Larkin", dates="1974", form="12 rhymed quatrains",
         why="The trees' annual greening is both consolation and rebuke: renewal happens, but it does not erase time. A sterner cousin to praise.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Trees%20Philip%20Larkin")], pd=False, ws=None),
    dict(num="5", title="Thistles", author="Ted Hughes", dates="1960", form="free verse",
         why="Creation here is fierce rather than gentle: thistles keep their own counsel and survive human interruption. Francis's brothers and sisters have teeth.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=Thistles%20Ted%20Hughes")], pd=False, ws=None),
    dict(num="6", title="The Raincoat", author="Ada Lim\u00f3n", dates="2018", form="free verse",
         why="A raincoat given from mother to daughter becomes a belated recognition of care that had quietly made a whole life possible.",
         difficulty="Moderate", links=[("Academy of American Poets", "https://poets.org/poem/raincoat")], pd=False, ws=None),
    dict(num="7", title="Dead Stars", author="Ada Lim\u00f3n", dates="2018", form="free verse",
         why="Beneath ordinary suburbia, people and trees bend toward survival. Its cosmic scale and ecological solidarity speak directly to the Canticle's family of creatures.",
         difficulty="Moderate", links=[("Academy of American Poets", "https://poets.org/anthology/women-color-1")], pd=False, ws=None),
    dict(num="8", title="The Orange", author="Wendy Cope", dates="1986", form="short free verse",
         why="A small fruit, shared in a hard season, becomes enough light for the day. Praise does not need a cathedral-sized occasion.",
         difficulty="Easy", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20Orange%20Wendy%20Cope")], pd=False, ws=None),
    dict(num="9", title="The House Was Quiet and the World Was Calm", author="Wallace Stevens", dates="1942", form="free verse",
         why="Reading at night becomes an act of such attention that mind, house, and world briefly settle into one order.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=The%20House%20Was%20Quiet%20and%20the%20World%20Was%20Calm%20Wallace%20Stevens")], pd=False, ws=None),
    dict(num="10", title="Messenger", author="Mary Oliver", dates="2007", form="free verse",
         why="The speaker's work is to love the world, to make a place for its notes, and to answer. It may be the clearest modern description of Franciscan vocation.",
         difficulty="Moderate", links=[("Poetry Foundation", "https://www.poetryfoundation.org/search?query=Messenger%20Mary%20Oliver")], pd=False, ws=None),
    dict(num="11", title="Instructions on Not Giving Up", author="Ada Lim\u00f3n", dates="2017", form="free verse",
         why="The return of leaves after damage is praise without sentimentality: the living world takes the hurt and continues opening.",
         difficulty="Moderate", links=[("Academy of American Poets", "https://poets.org/poem/instructions-not-giving")], pd=False, ws=None),
],
}

FURTHER = {
"a": [
    ("Psalm 139 (KJV), vv. 7\u201312", "\u201cWhither shall I flee from thy presence\u201d is the literal source text of Thompson's whole conceit. Public domain, in any Bible."),
    ("R. S. Thomas, \u201cThe Bright Field\u201d (1975)", "The pearl of great price as a lit field you drove past. In copyright."),
    ("Denise Levertov, \u201cThe Avowal\u201d (1981)", "Free fall into grace. In copyright."),
    ("Hopkins, \u201cPied Beauty\u201d and \u201cAs Kingfishers Catch Fire\u201d", "If you take to Hopkins, these two next."),
],
"b": [
    ("Naomi Shihab Nye, \u201cThe Art of Disappearing\u201d (1995)", "Permission to decline the party. \u201cWalk around feeling like a leaf.\u201d"),
    ("Naomi Shihab Nye, \u201cBurning the Old Year\u201d", "Three stanzas on what is flammable in a year and what isn't."),
    ("Raymond Carver, \u201cLate Fragment\u201d (1989)", "Five lines. Did you get what you wanted from this life, even so. Learnable in ninety seconds; stays for decades."),
    ("Czes\u0142aw Mi\u0142osz, \u201cGift\u201d", "A short poem about a morning with no envy in it. Nearly perfect."),
    ("Seamus Heaney, \u201cPostscript\u201d (1996)", "The Flaggy Shore, wind and light, being caught off guard and blown open."),
    ("W. S. Merwin, \u201cThanks\u201d (1988)", "Gratitude spoken into catastrophe. Relentless."),
    ("Rilke, \u201cGo to the Limits of Your Longing\u201d (trans. Barrows &amp; Macy, 1996)",
     "God speaking, telling you to let everything happen: beauty and terror, just keep going. "
     "<strong>Note:</strong> the German original is public domain but this translation is not, and <em>the title is "
     "the translators' invention</em> \u2014 Rilke's poem is untitled. Translations diverge enormously here. "
     "If you memorize it you are memorizing a translator's poem as much as Rilke's."),
    ("Mary Oliver, \u201cWild Geese\u201d (1986)", "You may already have it."),
    ("Ross Gay, \u201cSorrow Is Not My Name\u201d (2011); Maggie Smith, \u201cGood Bones\u201d (2016)", ""),
],
"c": [
    ("Dickinson, \u201cI heard a Fly buzz \u2014 when I died\u201d (Fr591)", "poetryfoundation.org/poems/45703"),
    ("Dickinson, \u201cMuch Madness is divinest Sense\u201d (Fr620)", "poetryfoundation.org/poems/51612"),
    ("Dickinson, \u201cSuccess is counted sweetest\u201d (Fr112)", "poetryfoundation.org/poems/45721"),
    ("Langston Hughes, \u201cDreams\u201d (1922)", "Eight lines. Hold fast to dreams. Hughes's estate is protective and his poems' status varies; read it via poetryfoundation.org."),
    ("Shakespeare, Sonnet 73", "\u201cThat time of year thou mayst in me behold\u201d \u2014 bare ruined choirs."),
    ("John Keats, \u201cWhen I have fears that I may cease to be\u201d (1818)", "Sonnet; ends alone on the shore of the wide world."),
    ("William Blake, \u201cThe Tyger\u201d (1794)", "And the opening quatrain of \u201cAuguries of Innocence,\u201d which is a complete poem on its own."),
    ("Robert Herrick, \u201cTo the Virgins, to Make Much of Time\u201d (1648)", ""),
    ("Stephen Crane, \u201cIn the Desert\u201d (1895)", "Ten lines, a creature eating its own heart. Unforgettable and slightly horrible."),
    ("William Wordsworth, \u201cThe world is too much with us\u201d (1807)", "Sonnet."),
],
}

# Entries promoted from the original “also worth your time” lists.  Keeping
# these as ordinary poem records means every output and tool sees them.
PROMOTED = {
"a": [
    dict(title="Psalm 139:7–12", author="King James Bible", dates="1611", form="6 lines (one per verse)",
         why="The direct scriptural ancestor of Thompson's flight from an inescapable presence.",
         difficulty="Easy", links=[("Bible Gateway (KJV)", "https://www.biblegateway.com/passage/?search=Psalm%20139%3A7-12&version=KJV")], pd=True, ws="Psalm 139 King James Version"),
    dict(title="The Bright Field", author="R. S. Thomas", dates="1975", form="short free verse",
         why="A glimpse of radiance becomes the pearl for which a life might be sold.", difficulty="Moderate",
         links=[("Poetry Archive", "https://poetryarchive.org/poem/bright-field/")], pd=False, ws=None),
    dict(title="The Avowal", author="Denise Levertov", dates="1981", form="short free verse",
         why="Free fall becomes an image of trust and grace.", difficulty="Easy–Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/48790/the-avowal")], pd=False, ws=None),
    dict(title="Pied Beauty", author="Gerard Manley Hopkins", dates="1877; pub. 1918", form="11 lines, curtal sonnet",
         why="Praise compressed into sprung rhythm: glory in everything dappled and changeable.", difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44399/pied-beauty")], pd=True, ws="Pied Beauty Hopkins"),
    dict(title="As Kingfishers Catch Fire", author="Gerard Manley Hopkins", dates="1877; pub. 1918", form="14 lines, sonnet",
         why="Each created thing speaks its own identity; the just person becomes the grace they enact.", difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44389/as-kingfishers-catch-fire")], pd=True, ws="As kingfishers catch fire Hopkins"),
],
"b": [
    dict(title="The Art of Disappearing", author="Naomi Shihab Nye", dates="1995", form="free verse",
         why="Permission to protect the inward life and decline the noise of performance.", difficulty="Moderate",
         links=[("Poets.org", "https://poets.org/poem/art-disappearing")], pd=False, ws=None),
    dict(title="Burning the Old Year", author="Naomi Shihab Nye", dates="1995", form="three stanzas, free verse",
         why="What burns easily in a year, and the few things that resist the fire.", difficulty="Easy–Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/57211/burning-the-old-year")], pd=False, ws=None),
    dict(title="Late Fragment", author="Raymond Carver", dates="1989", form="5 lines, free verse",
         why="A final accounting of whether one felt beloved and needed by life.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/58074/late-fragment")], pd=False, ws=None),
    dict(title="Gift", author="Czesław Miłosz", dates="1971", form="short free verse",
         why="A day without envy or pain, received without needing to possess it.", difficulty="Easy–Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/49458/gift")], pd=False, ws=None),
    dict(title="Postscript", author="Seamus Heaney", dates="1996", form="free verse",
         why="Wind and light catch the guarded heart off guard and blow it open.", difficulty="Moderate",
         links=[("Poetry Archive", "https://poetryarchive.org/poem/postscript/")], pd=False, ws=None),
    dict(title="Thanks", author="W. S. Merwin", dates="1988", form="free verse",
         why="Gratitude repeated inside catastrophe, without pretending catastrophe away.", difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/57937/thanks")], pd=False, ws=None),
    dict(title="Go to the Limits of Your Longing", author="Rainer Maria Rilke", dates="Book of Hours; Barrows/Macy trans. 1996", form="untitled poem in translation",
         why="Let everything happen—beauty and terror—and continue. The famous English title belongs to the translators.", difficulty="Moderate",
         links=[("Poetry Chaikhana (translation page)", "https://www.poetry-chaikhana.com/Poets/R/RilkeRainerM/GoToLimits/index.html")], pd=False, ws=None),
    dict(title="Wild Geese", author="Mary Oliver", dates="1986", form="18 lines, free verse",
         why="Belonging offered without a prerequisite of goodness.", difficulty="Moderate",
         links=[("Library of Congress guide", "https://www.loc.gov/programs/poetry-and-literature/poet-laureate/poet-laureate-projects/poetry-180/all-poems/item/poetry-180-133/wild-geese/")], pd=False, ws=None),
    dict(title="Sorrow Is Not My Name", author="Ross Gay", dates="2011", form="free verse",
         why="Joy and grief held together as a refusal to let sorrow own the whole world.", difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/92472/sorrow-is-not-my-name")], pd=False, ws=None),
    dict(title="Good Bones", author="Maggie Smith", dates="2016", form="free verse",
         why="The terrible world presented to children through the language of a hopeful sales pitch.", difficulty="Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/89897/good-bones")], pd=False, ws=None),
],
"c": [
    dict(title="I heard a Fly buzz — when I died —", author="Emily Dickinson", dates="Fr591; pub. 1896", form="16 lines, hymn meter",
         why="A single ordinary interruption carries an entire deathbed scene.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/45703/i-heard-a-fly-buzz-when-i-died-591")], pd=True, ws="I heard a Fly buzz when I died Dickinson"),
    dict(title="Much Madness is divinest Sense —", author="Emily Dickinson", dates="Fr620; pub. 1890", form="8 lines, hymn meter",
         why="One paradox sustained with frightening social clarity.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/51612/much-madness-is-divinest-sense-620")], pd=True, ws="Much Madness is divinest Sense Dickinson"),
    dict(title="Success is counted sweetest", author="Emily Dickinson", dates="Fr112; pub. 1864", form="12 lines, hymn meter",
         why="Defeat is made the condition for understanding victory.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/45721/success-is-counted-sweetest-112")], pd=True, ws="Success is counted sweetest Dickinson"),
    dict(title="Dreams", author="Langston Hughes", dates="1922", form="8 lines, two quatrains",
         why="A compact imperative whose two images make it almost impossible to forget.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/150995/dreams-5d767850da976")], pd=True, ws="Dreams Langston Hughes"),
    dict(title="Sonnet 73: That time of year thou mayst in me behold", author="William Shakespeare", dates="1609", form="14 lines, Shakespearean sonnet",
         why="Three images of approaching death narrow toward a final claim for love.", difficulty="Easy–Moderate",
         links=[("Poets.org", "https://poets.org/poem/time-year-thou-mayst-me-behold-sonnet-73")], pd=True, ws="Shakespeare Sonnet 73"),
    dict(title="When I have fears that I may cease to be", author="John Keats", dates="1818; pub. 1848", form="14 lines, Shakespearean sonnet",
         why="Fear of unwritten work and unlived love dissolves at the edge of the world.", difficulty="Easy–Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/44488/when-i-have-fears-that-i-may-cease-to-be")], pd=True, ws="When I have fears Keats"),
    dict(title="The Tyger", author="William Blake", dates="1794", form="24 lines, six quatrains",
         why="A sequence of questions makes terror and wonder share one unforgettable image.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/43687/the-tyger")], pd=True, ws="The Tyger William Blake"),
    dict(title="Auguries of Innocence (opening)", author="William Blake", dates="written c. 1803; pub. 1863", form="4 lines, opening quatrain",
         why="Four lines hold infinity and eternity inside the smallest visible things.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/43650/auguries-of-innocence")], pd=True, ws="Auguries of Innocence Blake"),
    dict(title="To the Virgins, to Make Much of Time", author="Robert Herrick", dates="1648", form="16 lines, four quatrains",
         why="The rosebud argument for mortality and action in its most memorable form.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/46546/to-the-virgins-to-make-much-of-time")], pd=True, ws="To the Virgins Herrick"),
    dict(title="In the Desert", author="Stephen Crane", dates="1895", form="10 lines, free verse",
         why="A creature eats its own bitter heart and insists that it likes it.", difficulty="Easy",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/46457/in-the-desert-56d2265793693")], pd=True, ws="In the Desert Stephen Crane"),
    dict(title="The world is too much with us", author="William Wordsworth", dates="1807", form="14 lines, Petrarchan sonnet",
         why="Estrangement from nature answered by a desperate wish for an older vision.", difficulty="Easy–Moderate",
         links=[("Poetry Foundation", "https://www.poetryfoundation.org/poems/45564/the-world-is-too-much-with-us")], pd=True, ws="The world is too much with us Wordsworth"),
],
}

RILKE = [
    ("Autumnal Day", "Herbsttag", "12 lines", "Ripeness, solitude, and the irreversible turn into autumn."),
    ("The Panther", "Der Panther", "12 lines", "Captivity rendered through exhausted sight and one final inward image."),
    ("Archaic Torso of Apollo", "Archäischer Torso Apollos", "14 lines, sonnet", "An artwork looks back and makes the demand: change your life."),
    ("Early Apollo", "Früher Apollo", "14 lines, sonnet", "The young god's face holds song before the full blaze of summer."),
    ("The Spanish Dancer", "Spanische Tänzerin", "18 lines", "A dancer becomes fire, then stamps the flame out."),
    ("Love Song", "Liebes-Lied", "17 lines", "Two solitudes seek a music that can hold them without erasing either."),
    ("The Poet", "Der Dichter", "8 lines", "The cost of a life surrendered to inward transformation."),
    ("Growing Blind", "Die Erblindende", "14 lines", "A woman's failing sight changes the space and people around her."),
    ("I Live My Life in Circles", "Ich lebe mein Leben in wachsenden Ringen", "9 lines", "A life circles the divine without needing to know whether it will arrive."),
    ("I Love My Life's Dark Hours", "Ich liebe meines Wesens Dunkelstunden", "12 lines", "Dark hours become the place where the self acquires depth and duration."),
    ("Extinguish My Eyes", "Lösch mir die Augen aus", "12 lines", "Every sense can be taken and the beloved still found inwardly."),
    ("Solitude", "Einsamkeit", "12 lines", "Loneliness rises from the streets like rain and gathers through the city."),
    ("Presaging", "Vorgefühl", "12 lines", "A coming storm is felt first as an immense unnamed disturbance."),
]

POEMS["d"] = []
for _i, (_title, _german, _form, _why) in enumerate(RILKE, 1):
    POEMS["d"].append(dict(num=str(_i), title=_title, author="Rainer Maria Rilke",
        dates=f"Jessie Lemont translation, <em>Poems</em> (1918); German: <em>{_german}</em>",
        form=_form, why=_why, difficulty="Moderate",
        links=[("Project Gutenberg: Poems (1918)", "https://www.gutenberg.org/ebooks/38594")],
        pd=True, ws=None, gutenberg_section=_title.upper()))

# In the plain-text Gutenberg edition these three Book of Hours poems have no
# separate headings; their first lines are the reliable extraction markers.
for _index, _marker, _form in (
    (8, "I live my life in circles that grow wide", "10 lines"),
    (9, "I love my life's dark hours", "14 lines"),
    (10, "Extinguish my eyes, I still can see you", "10 lines"),
):
    POEMS["d"][_index]["gutenberg_section"] = _marker
    POEMS["d"][_index]["gutenberg_marker_is_line"] = True
    POEMS["d"][_index]["form"] = _form

for _cid, _entries in PROMOTED.items():
    _start = len(POEMS[_cid])
    for _offset, _poem in enumerate(_entries, 1):
        _poem.setdefault("seed", False)
        _poem["num"] = str(_start + _offset - 1)
        POEMS[_cid].append(_poem)

# Nothing remains a second-class recommendation after promotion.
FURTHER = {c["id"]: [] for c in CATEGORIES}


def all_poems():
    for cat in CATEGORIES:
        for p in POEMS[cat["id"]]:
            yield cat, p


def public_domain_poems():
    return [(c, p) for c, p in all_poems() if p.get("pd")]


def slug(cat_id, poem):
    n = poem["num"].replace("\u00a7", "s")
    return f"{cat_id}{n}"
