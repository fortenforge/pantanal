#!/usr/bin/env python3
import json
import os
import datetime
from PIL import Image

with open('/home/antigravity/fortenforge/pantanal/album_catalog.json', 'r', encoding='utf-8') as f:
    catalog = {item['index']: item for item in json.load(f)}

os.makedirs('/home/antigravity/fortenforge/pantanal/media/crops', exist_ok=True)

# (species_title, scientific_name, crop_focus_xy_and_zoom, human_caption)
# crop_focus: (cx, cy, zoom) where cx, cy in [0..1] is the subject center and zoom >= 1.0 tightens the crop
ANNOTATIONS = {
    # --- 1. BEAUTIFUL (10 items) ---
    128: (
        "Toco Toucan",
        "Ramphastos toco",
        (0.42, 0.45, 1.18),
        "Look closely at that electric cobalt-blue eye ring surrounding a deep violet-blue iris. Even with an oversized tangerine bill that makes up a third of its length—earning it the affectionate nickname 'the flying banana' in flight—the bill is a marvel of lightweight keratin honeycomb that radiates excess body heat."
    ),
    281: (
        "Chestnut-eared Aracari",
        "Pteroglossus castanotis",
        (0.55, 0.45, 1.35),
        "Smaller and sleeker than its Toco cousin, the Chestnut-eared Aracari sports a serrated, two-toned bill, a rich mahogany ear patch, and a bold crimson band across its bright yellow belly."
    ),
    264: (
        "Blue-crowned Trogon",
        "Trogon curucui",
        (0.60, 0.52, 1.45),
        "Perched upright and motionless in the mid-story shade, the male Blue-crowned Trogon flashes an iridescent sapphire hood, a lime-yellow eye ring, and a vivid vermilion belly separated by a crisp white breast band."
    ),
    400: (
        "Surucua Trogon",
        "Trogon surrucura",
        (0.50, 0.48, 1.45),
        "Spotted in the Atlantic Forest around Iguazú clinging directly at the entrance of its excavated nest cavity in a decaying tree trunk—showing off its iridescent blue-green back and white-tipped tail."
    ),
    153: (
        "Rufous-tailed Jacamar",
        "Galbula ruficauda",
        (0.48, 0.45, 1.35),
        "Often mistaken at first glance for a giant hummingbird, this male Rufous-tailed Jacamar is an aerial insect assassin—perching on a quiet branch with its needle-sharp bill poised to snatch butterflies mid-flight."
    ),
    110: (
        "Ringed Kingfisher",
        "Megaceryle torquata",
        (0.50, 0.50, 1.10),
        "The largest kingfisher in the Americas! In this video, a male Ringed Kingfisher grips a freshly caught fish in its heavy dagger bill, methodically whacking its prize against the branch before swallowing it headfirst."
    ),
    146: (
        "Green Kingfisher",
        "Chloroceryle americana",
        (0.48, 0.48, 1.35),
        "The male Green Kingfisher wears a bottle-green coat and a warm, burnished rufous breastband—leaning forward intently over a quiet backwater channel waiting for a minnow to surface."
    ),
    398: (
        "Swallow Tanager",
        "Tersina viridis",
        (0.46, 0.52, 1.50),
        "With his electric turquoise plumage, jet-black face mask, and barred flanks, the male Swallow Tanager is built for both fruit-eating and hawking insects on the wing."
    ),
    367: (
        "Blue Dacnis",
        "Dacnis cayana",
        (0.38, 0.52, 1.45),
        "Glowing in saturated turquoise and velvet black with bright coral legs as he pauses among the Atlantic Forest foliage."
    ),
    19: (
        "Red-crested Cardinal",
        "Paroaria coronata",
        (0.48, 0.48, 1.45),
        "With its scarlet punk-rock crest, snow-white breast, and tailored slate-gray back, the Red-crested Cardinal brings unmistakable flair to the open savannas of the Pantanal."
    ),

    # --- 2. BIZARRE (10 items) ---
    409: (
        "Great Potoo",
        "Nyctibius grandis",
        (0.52, 0.46, 1.15),
        "Watch the zoom reveal! From a distance it looks like nothing more than a dead stub on a bare tree—until the camera zooms in to reveal a Great Potoo frozen upright with its eyes shut, peering through tiny 'magic slits' in its eyelids to watch passing intruders without breaking its bark camouflage."
    ),
    277: (
        "Red-legged Seriema",
        "Cariama cristata",
        (0.52, 0.50, 1.25),
        "Looking and acting like a feathered velociraptor, the Red-legged Seriema is the closest living relative of the extinct giant 'terror birds' (Phorusrhacids). It strides across the savanna on long salmon-red legs, sports a fountain-like spray of feathers at the base of its bill, and carries a sickle-like claw on its second toe."
    ),
    242: (
        "Undulated Tinamou",
        "Crypturellus undulatus",
        (0.50, 0.50, 1.10),
        "Far more often heard than seen! Its haunting, three-note whistled song is the signature soundtrack of the Pantanal, yet catching this football-shaped, cryptically barred member of one of Earth's most ancient bird lineages strolling in the open is a true birding prize."
    ),
    104: (
        "Wattled Jacana",
        "Jacana jacana",
        (0.50, 0.50, 1.10),
        "Watch its comical, high-stepping stride across the floating vegetation—and look at the size of those toes! The Wattled Jacana's impossibly elongated toes distribute its weight like snowshoes across lily pads, while females fiercely defend harems of males who do all the egg incubation and chick-rearing."
    ),
    175: (
        "Jabiru",
        "Jabiru mycteria",
        (0.55, 0.52, 1.30),
        "A Jabiru resting flat on its 'heels' looks almost comical—because a bird's backward-bending 'knee' is actually its ankle joint, when this five-foot-tall stork sits down to rest, its long tarsus stretches out flat along the sandbar!"
    ),
    5: (
        "Greater Rhea",
        "Rhea americana",
        (0.50, 0.50, 1.10),
        "South America's largest bird! Among Greater Rheas, a single male builds the ground nest, incubates eggs laid by up to a dozen females, and then single-handedly shepherds this bustling kindergarten of striped chicks across the savanna."
    ),
    132: (
        "Southern Screamer",
        "Chauna torquata",
        (0.50, 0.50, 1.10),
        "Related to ducks and geese despite looking like prehistoric turkeys with hawk-like bills and sharp bony wing-spurs, this pair of Southern Screamers leads their fluffy yellow-downed chicks through the marsh grass."
    ),
    113: (
        "Sunbittern",
        "Eurypyga helias",
        (0.50, 0.52, 1.35),
        "So evolutionarily distinct it belongs to its own order alongside New Caledonia's Kagu, the Sunbittern stalks quietly along shady creek banks until it spreads its wings to flash two startling 'giant eyespots' of chestnut, gold, and black."
    ),
    206: (
        "Guira Cuckoo",
        "Guira guira",
        (0.46, 0.46, 1.30),
        "With its unruly, spiky orange crest, pale yellow eye, and disheveled streaked plumage, the communal Guira Cuckoo looks perpetually startled as it clambers over tangled vines."
    ),
    39: (
        "Bare-faced Curassow",
        "Crax fasciolata",
        (0.48, 0.48, 1.25),
        "The male Bare-faced Curassow struts in formal jet-black attire with a snowy white belly, a tightly curled punk crest, and a bright sulfur-yellow cere at the base of his bill."
    ),

    # --- 3. HERONS (9 items) ---
    13: (
        "Great Egret",
        "Ardea alba",
        (0.50, 0.50, 1.10),
        "An unforgettable drama along the wetland edge: a Great Egret wrestles a writhing water snake in its dagger-like yellow bill, repeatedly repositioning its slippery catch before gulping it down."
    ),
    20: (
        "Whistling Heron",
        "Syrigma sibilatrix",
        (0.50, 0.48, 1.30),
        "Often called the most beautiful heron in the world, the Whistling Heron looks hand-painted in soft buttery yellows, powder-blue facial skin, a pink-and-black bill, and cinnamon neck feathers."
    ),
    212: (
        "Capped Heron",
        "Pilherodius pileatus",
        (0.48, 0.48, 1.30),
        "Unmistakable with its electric cobalt-blue face and bill, jet-black cap, long creamy crown plumes, and a soft warm wash across its breast."
    ),
    187: (
        "Boat-billed Heron",
        "Cochlearius cochlearius",
        (0.48, 0.48, 1.30),
        "With its enormous dark eyes built for night hunting and a wide, shoe-shaped scoop of a bill sensitive to the slightest vibration in murky water, the Boat-billed Heron roosts quietly in dense overhanging tangles by day."
    ),
    283: (
        "Rufescent Tiger-Heron",
        "Tigrisoma lineatum",
        (0.46, 0.45, 1.25),
        "The adult Rufescent Tiger-Heron wears a rich, unbarred mahogany-chestnut head and neck with a vertical white-and-brown stripe running down its throat."
    ),
    210: (
        "Rufescent Tiger-Heron",
        "Tigrisoma lineatum",
        (0.45, 0.52, 1.30),
        "Look how different the juvenile plumage is from the adult! Young Rufescent Tiger-Herons are covered head-to-tail in bold tawny-and-black 'tiger stripes' that blend seamlessly into dried reeds and grass."
    ),
    97: (
        "Striated Heron",
        "Butorides striata",
        (0.50, 0.50, 1.10),
        "Crouched low and horizontal at the water's edge right beside basking caimans, this compact Striated Heron freezes with laser focus before striking at passing small fish."
    ),
    92: (
        "Little Blue Heron",
        "Egretta caerulea",
        (0.50, 0.50, 1.30),
        "Draped in slate-blue body feathers with a deep maroon-purple neck and a two-toned bill, stalking methodically through the flooded hyacinths."
    ),
    95: (
        "Cocoi Heron",
        "Ardea cocoi",
        (0.50, 0.48, 1.25),
        "South America's tall, stately counterpart to the Great Blue Heron—distinguished by its clean snow-white neck, jet-black cap, and bold black flank stripes."
    ),

    # --- 4. PARROTS (10 items) ---
    81: (
        "Hyacinth Macaw",
        "Anodorhynchus hyacinthinus",
        (0.50, 0.50, 1.10),
        "The largest flying parrot on Earth! Watching this pair of cobalt-blue giants preening each other's feathers—with their sunny yellow eye rings and bare yellow grin-patches framing bills strong enough to crack rock-hard acuri palm nuts—was pure Pantanal magic."
    ),
    0: (
        "Blue-and-yellow Macaw",
        "Ara ararauna",
        (0.48, 0.42, 1.20),
        "The very first photo of the trip: a Blue-and-yellow Macaw clinging to the rim of its hollowed palm-trunk nest cavity, glowing turquoise-blue above and golden-saffron below."
    ),
    2: (
        "Red-shouldered Macaw",
        "Diopsittaca nobilis",
        (0.50, 0.48, 1.35),
        "At just 12 inches long, the Red-shouldered Macaw is the smallest of all macaws—mostly emerald green with a slate-blue forehead, bare white facial skin, and a flash of scarlet at the bend of the wing."
    ),
    240: (
        "Yellow-collared Macaw",
        "Primolius auricollis",
        (0.50, 0.48, 1.35),
        "A pair of Yellow-collared Macaws perched high in a bare treetop, showing the bright golden-yellow nape collar and dark facial mask characteristic of this agile mini-macaw."
    ),
    155: (
        "Turquoise-fronted Amazon",
        "Amazona aestiva",
        (0.50, 0.50, 1.10),
        "A bonded pair of Turquoise-fronted Amazons vocalizing and clambering through the branches, flashing their turquoise foreheads and yellow cheeks."
    ),
    332: (
        "Scaly-headed Parrot",
        "Pionus maximiliani",
        (0.50, 0.48, 1.35),
        "With bronze-rimmed neck feathers that create a subtle scaled texture and a washed violet breastband, this Scaly-headed Parrot blends right into the leafy canopy at Iguazú."
    ),
    23: (
        "Monk Parakeet",
        "Myiopsitta monachus",
        (0.48, 0.50, 1.40),
        "The only parrot in the world that weaves massive communal stick nests rather than nesting in tree cavities—often building sprawling apartment complexes directly into the underside of Jabiru stork nests!"
    ),
    57: (
        "Peach-fronted Parakeet",
        "Eupsittula aurea",
        (0.50, 0.48, 1.30),
        "A trio of Peach-fronted Parakeets huddled together, showing off their warm apricot foreheads and golden orbital rings."
    ),
    123: (
        "Nanday Parakeet",
        "Aratinga nenday",
        (0.50, 0.50, 1.10),
        "Instantly recognizable by their ink-black hoods, pale blue breast wash, and feathery scarlet 'thigh socks' as they chatter in the palm tops."
    ),
    127: (
        "Yellow-chevroned Parakeet",
        "Brotogeris chiriri",
        (0.50, 0.50, 1.10),
        "Small, sleek lime-green parakeets with a bright slash of canary-yellow along the folded wing edge."
    ),

    # --- 5. HUMMINGBIRDS (10 items) ---
    362: (
        "Gilded Hummingbird",
        "Hylocharis chrysura",
        (0.46, 0.52, 1.30),
        "Frozen in mid-air at a pink blossom, the Gilded Hummingbird glows like burnished copper-gold from crown to tail, offset by a bright coral-red bill tipped in black."
    ),
    358: (
        "Planalto Hermit",
        "Phaethornis pretrei",
        (0.48, 0.48, 1.25),
        "Caught mid-hover with its long, white-tipped central tail feathers flared and its decurved bill poised—hermits are trap-line feeders that follow a memorized circuit of forest flowers every day."
    ),
    235: (
        "Glittering-throated Emerald",
        "Chionomesa fimbriata",
        (0.46, 0.52, 1.40),
        "Perched cleanly on a slender twig in the Pantanal, catching the light across its metallic emerald throat and coral-red lower mandible."
    ),
    353: (
        "Black-throated Mango (Male)",
        "Anthracothorax nigricollis",
        (0.50, 0.50, 1.10),
        "Hovering in slow-motion brilliance: the male Black-throated Mango displays a velvet-black center stripe bordered by glowing turquoise-blue along the sides of his neck."
    ),
    368: (
        "Black-throated Mango (Female)",
        "Anthracothorax nigricollis",
        (0.52, 0.55, 1.30),
        "Look at the dramatic central black stripe running down the female Black-throated Mango's snow-white underparts as she hovers with wings blurred at the feeder."
    ),
    355: (
        "Black Jacobin",
        "Florisuga fusca",
        (0.50, 0.50, 1.10),
        "Dressed in sleek jet-black plumage, the Black Jacobin flares a startling snow-white tail fan in flight while hovering around the garden flowers."
    ),
    364: (
        "Versicolored Emerald",
        "Chrysuronia versicolor",
        (0.48, 0.52, 1.40),
        "True to its name, the Versicolored Emerald shifts from glittering aquamarine on the cheeks to emerald green on the back and a pale-centered throat."
    ),
    363: (
        "Swallow-tailed Hummingbird",
        "Eupetomena macroura",
        (0.43, 0.56, 1.25),
        "With its deeply forked, scissor-like cobalt tail spread in a dramatic V and a glowing violet-blue hood, the large and assertive Swallow-tailed Hummingbird dominates prime flowering perches."
    ),
    369: (
        "Glittering-bellied Emerald",
        "Chlorostilbon lucidus",
        (0.48, 0.50, 1.35),
        "Iridescent emerald-gold from throat to belly with a bright red-based bill and a dark steel-blue forked tail."
    ),
    378: (
        "Violet-capped Woodnymph",
        "Thalurania glaucopis",
        (0.48, 0.50, 1.35),
        "An Atlantic Forest gem sporting a glowing violet-purple cap against a brilliant emerald-green throat and breast."
    ),

    # --- 6. JAGUARS (10 items) ---
    169: (
        "Jaguar — Riverbank Sentinel",
        "Panthera onca",
        (0.52, 0.48, 1.25),
        "Seated regally in the lush green riverbank grass of the northern Pantanal, scanning the opposite shore with calm authority. The Pantanal hosts the highest density of—and physically largest—jaguars on Earth."
    ),
    164: (
        "Jaguar — On the Prowl",
        "Panthera onca",
        (0.50, 0.50, 1.25),
        "Muscles coiled, tail curled cleanly upward, and jaws slightly parted as it strides along the brushy levee—showing the intricate black rosettes with central spots that are unique as fingerprints to each individual jaguar."
    ),
    159: (
        "Jaguar — Framed in the Roots",
        "Panthera onca",
        (0.54, 0.48, 1.25),
        "Tucked among twisted gallery-forest roots behind a foreground curtain of floating water hyacinths, blending effortlessly into the dappled light and shadow."
    ),
    142: (
        "Jaguar — Resting on Fallen Timber",
        "Panthera onca",
        (0.55, 0.50, 1.25),
        "Draped across a sun-bleached log on the riverbank with heavy forepaws crossed and golden eyes locked directly toward our boat."
    ),
    171: (
        "Jaguar — Submerged Stealth",
        "Panthera onca",
        (0.52, 0.52, 1.30),
        "Unlike most big cats, Pantanal jaguars are completely amphibious hunters that patrol the rivers for capybaras and caimans—here slipping silently through the shallows with only its ears, eyes, and nose breaking the surface."
    ),
    189: (
        "Jaguar — Stepping onto the Mudbank",
        "Panthera onca",
        (0.48, 0.52, 1.25),
        "Stepping out of the river onto the slick mudbank, wearing a conservation research collar used by biologists to study territory size and movement corridors across the Pantanal."
    ),
    160: (
        "Jaguar — Prowling Behind Hyacinths",
        "Panthera onca",
        (0.50, 0.50, 1.10),
        "Over a full minute of watching a wild jaguar pace silently through the tangled root buttresses and floating mats of water hyacinth along the river's edge."
    ),
    168: (
        "Jaguar — In the Tall Grass",
        "Panthera onca",
        (0.50, 0.50, 1.10),
        "Up-close motion in the riverbank reeds, showing the sheer power of its broad skull and shoulders—evolving the strongest bite force relative to body size of any big cat to pierce caiman skulls and turtle shells."
    ),
    173: (
        "Jaguar — River Crossing",
        "Panthera onca",
        (0.50, 0.50, 1.10),
        "Swimming effortlessly across the open river current, head held steady above the water as it angles toward the far bank."
    ),
    188: (
        "Jaguar — Swimming Close-up",
        "Panthera onca",
        (0.50, 0.50, 1.10),
        "A tight view of a jaguar cutting through the amber ripples of the river with powerful, silent strokes."
    ),

    # --- 7. MAMMALS (10 items) ---
    258: (
        "Giant Anteater",
        "Myrmecophaga tridactyla",
        (0.50, 0.50, 1.20),
        "Notice its massive curved foreclaws! To keep those four-inch digging blades razor-sharp for ripping open rock-hard termite mounds—and defending itself against jaguars—the Giant Anteater folds its claws inward and walks on its padded knuckles under a bushy banner of a tail."
    ),
    245: (
        "Six-banded Armadillo",
        "Euphractus sexcinctus",
        (0.50, 0.50, 1.10),
        "Unlike the nocturnal Nine-banded Armadillo, the sandy-yellow Six-banded Armadillo is often active right in the middle of the day, trotting busily through the dry grass in search of roots, fruit, and insects."
    ),
    50: (
        "Ocelot",
        "Leopardus pardalis",
        (0.50, 0.50, 1.10),
        "A thrilling nocturnal encounter! Illuminated briefly in the night spotlight, an agile Ocelot scales a vertical tree trunk before pausing in the branches overhead."
    ),
    66: (
        "Crab-eating Fox",
        "Cerdocyon thous",
        (0.48, 0.50, 1.30),
        "Pausing in the dusty track to look back over its shoulder, the Crab-eating Fox switches its diet with the seasons—hunting crabs and frogs on the floodplains during the wet season and switching to fruits and insects when the waters recede."
    ),
    350: (
        "Hooded Capuchin",
        "Sapajus cay",
        (0.48, 0.45, 1.30),
        "With dark sideburns framing an expressive face and tufted dark hair resembling a capuchin friar's hood, this clever primate peers down curiously from the leafy branches."
    ),
    192: (
        "Black-and-gold Howler Monkey",
        "Alouatta caraya",
        (0.50, 0.50, 1.10),
        "Adult male Black-and-gold Howler Monkeys turn jet-black as they mature (while females and juveniles stay golden-blonde), and their deep, resonant dawn chorus carries for up to three miles through the forest."
    ),
    94: (
        "Capybara & Babies",
        "Hydrochoerus hydrochaeris",
        (0.50, 0.50, 1.10),
        "The world's largest rodent living its best life at the edge of a lily-covered lagoon, accompanied by a cluster of miniature youngsters."
    ),
    98: (
        "Three-Day-Old Capybara Pups",
        "Hydrochoerus hydrochaeris",
        (0.50, 0.52, 1.30),
        "These tiny capybara pups are only three days old! Precocial from birth, capybara babies are born with a full coat of fur, open eyes, and the ability to walk and nibble grass within hours."
    ),
    41: (
        "South American Coati",
        "Nasua nasua",
        (0.52, 0.48, 1.25),
        "Trotting across the clearing with its banded tail held straight up like a periscope so troop members can spot each other in tall grass while snuffling the soil with its flexible snout."
    ),
    193: (
        "Proboscis Bats",
        "Rhynchonycteris naso",
        (0.50, 0.50, 1.35),
        "Look closely along the vertical tree trunk: half a dozen tiny Proboscis Bats are lined up nose-to-tail in a neat row! Their grizzled fur and pale back stripes mimic lichens on the bark, and when a breeze blows they even sway in unison like loose bark flakes."
    ),

    # --- 8. WOODPECKERS (10 items) ---
    288: (
        "Crimson-crested Woodpecker (Pair)",
        "Campephilus melanoleucos",
        (0.55, 0.45, 1.25),
        "Both sexes together on the same V-shaped tree fork! The male on the right has a completely crimson head and malar stripe, while the female on the left sports a black central crown and a sweeping white cheek stripe."
    ),
    218: (
        "Cream-colored Woodpecker",
        "Celeus flavus",
        (0.45, 0.46, 1.30),
        "Dressed almost entirely in soft, buttery cream-yellow plumage with chestnut-brown wings and a bold crimson malar ('mustache') patch, this Cream-colored Woodpecker peers over a lichen-crusted branch."
    ),
    58: (
        "Pale-crested Woodpecker",
        "Celeus lugubris",
        (0.48, 0.48, 1.35),
        "Crowned with a bushy straw-yellow crest against a dark, golden-barred back, this female Pale-crested Woodpecker uses her chisel bill to excavate an arboreal termite nest."
    ),
    231: (
        "Campo Flicker",
        "Colaptes campestris",
        (0.50, 0.50, 1.35),
        "Perched atop a weathered fence post, the terrestrial Campo Flicker displays its bright golden-yellow collar and cheeks—spending most of its day on the ground raiding ant hills."
    ),
    298: (
        "White Woodpecker",
        "Melanerpes candidus",
        (0.45, 0.25, 1.85),
        "Snow-white head and belly, jet-black back, and a striking golden-yellow eye ring and nape patch—White Woodpeckers travel in vocal family groups in search of wild honey and wasp larvae."
    ),
    309: (
        "White-spotted Woodpecker",
        "Dryobates spilogaster",
        (0.56, 0.48, 1.40),
        "Clinging vertically to a lichen-dappled trunk at Iguazú, intricately barred and spotted in olive, white, and black."
    ),
    313: (
        "Ochre-collared Piculet",
        "Picumnus temminckii",
        (0.48, 0.50, 1.45),
        "Hardly larger than a walnut, piculets are miniature woodpeckers with soft, unstiffened tails that hop around thin vines like nuthatches while tapping for tiny ants."
    ),
    377: (
        "Yellow-fronted Woodpecker",
        "Melanerpes flavifrons",
        (0.76, 0.36, 1.65),
        "One of the most colorful woodpeckers of the Atlantic Forest, combining a golden forehead and throat, crimson crown, black eye-mask, and zebra-barred back."
    ),
    379: (
        "Blond-crested Woodpecker",
        "Celeus flavescens",
        (0.50, 0.48, 1.35),
        "Crowned with a lush, silky cream-blonde crest against a jet-black breast and barred wings in the Atlantic Forest."
    ),
    54: (
        "Great Rufous Woodcreeper",
        "Xiphocolaptes major",
        (0.50, 0.48, 1.30),
        "A giant among woodcreepers! With its heavy, slightly decurved bill and cinnamon-rufous plumage, this pair hitches up tree trunks probing beneath loose bark for large arthropods and small frogs."
    ),

    # --- 9. RAPTORS (10 items) ---
    121: (
        "Savanna Hawk",
        "Buteogallus meridionalis",
        (0.48, 0.45, 1.30),
        "Long-legged and richly dressed in warm cinnamon-rufous plumage, this Savanna Hawk surveys the open floodplain from a gnarled dead snag, ready to drop down on crabs, snakes, or rodents."
    ),
    14: (
        "Black-collared Hawk",
        "Busarellus nigricollis",
        (0.48, 0.48, 1.35),
        "Unmistakable with its snow-white head, bold black throat crescent, and deep chestnut body—its soles are covered in tiny spiny spicules for gripping slippery fish in shallow Pantanal pools."
    ),
    12: (
        "Great Black Hawk",
        "Buteogallus urubitinga",
        (0.50, 0.48, 1.35),
        "A powerful, broad-winged raptor in coal-black adult plumage with bright yellow lores and long yellow legs perched along the river margin."
    ),
    136: (
        "Crane Hawk",
        "Geranospiza caerulescens",
        (0.50, 0.48, 1.35),
        "Slate-gray with blazing orange-red legs that possess a unique 'double-jointed' intertarsal articulation, allowing the Crane Hawk to reach inside tree holes and bromeliads in any direction to extract hiding prey."
    ),
    135: (
        "Snail Kite",
        "Rostrhamus sociabilis",
        (0.48, 0.46, 1.30),
        "Look at that extreme, needle-sharp hooked upper mandible—curved to the exact geometry needed to slip inside an apple snail's shell and sever its muscle without cracking the shell!"
    ),
    224: (
        "Bat Falcon",
        "Falco rufigularis",
        (0.42, 0.55, 1.40),
        "A compact, bullet-fast falcon perched on an exposed high snag—slate-black above with a creamy throat, finely barred breast, and rich rufous 'thighs'—waiting to hunt bats, swifts, and hummingbirds at dusk."
    ),
    140: (
        "Crested Caracara",
        "Caracara plancus",
        (0.50, 0.50, 1.10),
        "A nervous Crested Caracara pacing and looking around warily—these intelligent, terrestrial falcons will boldly walk right up to carcasses and riverbanks on their long yellow legs."
    ),
    213: (
        "Turkey Vulture",
        "Cathartes aura ruficollis",
        (0.50, 0.48, 1.35),
        "Notice the distinct band of creamy-white skin across the back of its red head and nape—a field mark specific to the South American subspecies (ruficollis) that you won't see on North American Turkey Vultures!"
    ),
    31: (
        "Ferruginous Pygmy-Owl",
        "Glaucidium brasilianum",
        (0.48, 0.48, 1.35),
        "Look closely at the two dark, white-bordered spots on the back of its head! Those 'false eyes' (ocelli) fool mobbing songbirds and larger predators into thinking this tiny, fierce diurnal owl is staring straight at them even when its back is turned."
    ),
    292: (
        "Burrowing Owl",
        "Athene cunicularia",
        (0.50, 0.50, 1.10),
        "Burrowing owls actually excavating their own burrow! Unlike the Burrowing Owls we see in the San Francisco Bay Area—which rely almost entirely on abandoned ground squirrel tunnels—South American Burrowing Owls frequently dig their own sandy burrows from scratch."
    ),

    # --- 10. WATERBIRDS & WADERS (10 items) ---
    150: (
        "Anhinga",
        "Anhinga anhinga",
        (0.48, 0.50, 1.20),
        "Because the Anhinga lacks waterproof oils on its feathers so it can dive silently without buoyancy, it must perch with its wings spread wide in a 'heraldic pose' to dry in the sun after spearing fish underwater."
    ),
    137: (
        "Maguari Stork",
        "Ciconia maguari",
        (0.50, 0.48, 1.30),
        "A striking cousin of the European White Stork, sporting crimson-orange facial skin around pale yellow eyes and a two-toned blue-and-red bill."
    ),
    27: (
        "Plumbeous Ibis",
        "Theristicus caerulescens",
        (0.50, 0.48, 1.30),
        "Dressed in silvery slate-gray with a bushy crest of elongated nape feathers, coral legs, and a fiery orange iris."
    ),
    139: (
        "Buff-necked Ibis",
        "Theristicus caudatus",
        (0.60, 0.48, 1.30),
        "With its warm cinnamon-buff head and neck, charcoal belly, and loud bugling calls, the Buff-necked Ibis forages across open pastures and dry savannas."
    ),
    106: (
        "Limpkin",
        "Aramus guarauna",
        (0.50, 0.48, 1.30),
        "Spotted in chocolate-and-white plumage along the marsh edge, the Limpkin's long bill curves slightly to the right at the tip so it can pry apple snails out of their dextrally coiled shells."
    ),
    93: (
        "Gray-cowled Wood-Rail",
        "Aramides cajaneus",
        (0.50, 0.50, 1.30),
        "Strutting boldly along the muddy bank with a slate-gray hood, olive back, bright yellow bill, and bubblegum-pink legs."
    ),
    143: (
        "Pied Plover",
        "Hoploxypterus cayanus",
        (0.50, 0.50, 1.35),
        "Dapper as a tuxedo on long scarlet stilts, the Pied Plover patrols sandy riverbars with its crisp black-and-white patterning and red eye-ring."
    ),
    262: (
        "Large-billed Tern",
        "Phaetusa simplex",
        (0.50, 0.50, 1.25),
        "A pair of Large-billed Terns showing off their heavy yellow bills and bold black-white-and-gray geometric wing panels found along South America's great river systems."
    ),
    276: (
        "Three Duck Species Together",
        "Dendrocygna viduata, D. autumnalis & Amazonetta brasiliensis",
        (0.50, 0.52, 1.20),
        "Three Neotropical waterfowl species side by side in one frame: White-faced Whistling-Ducks with their stark white masks, Black-bellied Whistling-Ducks with coral bills, and Brazilian Teal."
    ),
    405: (
        "Black-fronted Piping-Guan",
        "Pipile jacutinga",
        (0.48, 0.48, 1.35),
        "An endangered jewel of the Atlantic Forest around Iguazú, sporting a black forehead, sky-blue eye patch, white crest, and bi-colored blue-and-red wattle."
    ),

    # --- 11. SONGBIRDS & FLYCATCHERS (10 items) ---
    9: (
        "Rufous Hornero",
        "Furnarius rufus",
        (0.50, 0.50, 1.35),
        "Argentina's national bird and an architectural genius: pairs carry thousands of mud-and-straw pellets to construct dome-shaped 'clay ovens' on fence posts and tree branches that bake rock-hard in the sun."
    ),
    89: (
        "Pale-legged Hornero",
        "Furnarius leucopus",
        (0.50, 0.50, 1.10),
        "Smaller and more richly colored than the Rufous Hornero, strutting along the muddy riverbank on pale pinkish legs with a bright white eyebrow."
    ),
    45: (
        "Greater Thornbird",
        "Phacellodomus ruber",
        (0.50, 0.50, 1.10),
        "Rufous-winged and yellow-eyed, the Greater Thornbird builds massive, multi-chambered hanging stick fortresses at the tips of branches."
    ),
    198: (
        "Barred Antshrike",
        "Thamnophilus doliatus",
        (0.50, 0.50, 1.10),
        "Watch his whole tail and crest tremble as this zebra-striped male Barred Antshrike belts out his accelerating, bouncing-ball song ending in an emphatic nasal twang!"
    ),
    190: (
        "Crested Oropendola Nests",
        "Psarocolius decumanus",
        (0.50, 0.50, 1.20),
        "Intricate teardrop baskets up to four feet long woven from plant fibers and suspended from high outer branches to keep eggs safe from climbing snakes and monkeys."
    ),
    84: (
        "Eight-Species Feeding Flock",
        "Mixed Ground Flock",
        (0.50, 0.50, 1.10),
        "Count all eight species sharing the ground in a single clip: Ruddy Ground Dove, White-tipped Dove, Scaled Dove, Shiny Cowbird, Giant Cowbird, Yellow-billed Cardinal, Saffron Finch, and Grayish Baywing!"
    ),
    312: (
        "Long-tailed Tyrant",
        "Colonia colonus",
        (0.45, 0.52, 1.45),
        "Silhouetted on a high dead snag with its pale cap and two extraordinary ribbon-like central tail streamers."
    ),
    232: (
        "Fork-tailed Flycatcher",
        "Tyrannus savana",
        (0.46, 0.50, 1.35),
        "Perched among tangled branches with its dramatic scissor-like tail streamers extending well past its body."
    ),
    418: (
        "Plush-crested Jay",
        "Cyanocorax chrysops",
        (0.50, 0.48, 1.35),
        "Perched alertly in the Atlantic Forest with its velvety black bristle-crest, glowing golden eye, sky-blue cheek patches, and white-tipped tail."
    ),
    75: (
        "Orange-backed Troupial",
        "Icterus croconotus",
        (0.50, 0.48, 1.35),
        "Blazing tangerine-orange and jet-black with a pale blue facial patch, the Orange-backed Troupial is as bold in personality as it is in color—and a master mimic of other birds' calls."
    ),

    # --- 12. INSECTS, REPTILES & FROGS (10 items) ---
    342: (
        "Hydaspes Eighty-eight Butterfly",
        "Callicore hydaspes",
        (0.45, 0.52, 1.30),
        "Nature's typography at Iguazú Falls: the underside of this butterfly's hindwing spells out a crisp, graphic '88' in black and white bordered by electric blue and carmine red!"
    ),
    415: (
        "Eighty-eight Butterfly on Hand",
        "Diaethria clymena",
        (0.68, 0.46, 1.75),
        "An Eighty-eight Butterfly landing right on the back of a hand along the Iguazú Falls walkway to sip trace minerals from the skin."
    ),
    410: (
        "Iridescent Leaf Beetle",
        "Chrysomelidae",
        (0.50, 0.48, 1.40),
        "Glowing like polished emerald, gold, and ruby enamel nestled inside the geometric ribbing of a tropical cecropia leaf."
    ),
    389: (
        "Twig-Girdler Long-horned Beetle",
        "Onciderini (Cerambycidae)",
        (0.50, 0.50, 1.25),
        "The adult female Long-horned Beetle uses her powerful mandibles to chew a precise, circular groove all the way around a living tree branch. This 'girdling' cuts off the flow of nutrients and sap—and we actually saw branches neatly cut off by this beetle along the trail!"
    ),
    413: (
        "Dead-Leaf Mimic Moth",
        "Noctuidae / Geometridae",
        (0.50, 0.50, 1.10),
        "Resting on a painted green post, this moth looks indistinguishable from a curled, dried autumn leaf—complete with a false midrib vein and tiny dark 'fungal spots'—until it flutters to life in the video!"
    ),
    416: (
        "Owl-Eyed Satyr Butterfly",
        "Taygetis / Satyrinae",
        (0.48, 0.50, 1.35),
        "Resting among lush fern fronds with a row of intricate, white-ringed eyespots along its chocolate-brown hindwing margin to deflect bird attacks away from its body."
    ),
    414: (
        "Tiger-Striped Butterfly",
        "Consul / Mechanitis",
        (0.52, 0.48, 1.35),
        "Basking on a sunlit leaf in the Atlantic Forest with bold tiger-orange, yellow, and black warning stripes."
    ),
    374: (
        "Jataí Stingless Bees",
        "Tetragonisca angustula",
        (0.50, 0.50, 1.10),
        "Tiny golden stingless bees hovering around their wax entrance tube! In late 2025 and 2026, select Amazonian municipalities in Peru (such as Satipo and Nauta) made history by granting native stingless bees legal rights as subjects with the right to exist and thrive."
    ),
    234: (
        "Yacare Caimans",
        "Caiman yacare",
        (0.50, 0.50, 1.20),
        "Dozens of Yacare Caimans basking nose-to-tail along a receding dry-season mudbank! Roughly ten million Yacare Caimans inhabit the Pantanal, forming the backbone of the wetland food web."
    ),
    68: (
        "Black-and-white Tegu",
        "Salvator merianae",
        (0.50, 0.50, 1.25),
        "A hefty, intelligent lizard up to four feet long basking in the sun—tegus are remarkable among reptiles for being able to raise their own internal body temperature by up to 10°C during the breeding season."
    ),

    # --- 13. IGUAZÚ FALLS & LANDSCAPES (8 items) ---
    420: (
        "Iguazú Cataracts — Upper Rim",
        "Iguazú National Park",
        (0.50, 0.50, 1.05),
        "Standing beside the thundering golden-brown torrents plunging over the basalt cliff edge into the misty gorge below."
    ),
    419: (
        "The Amphitheater of Iguazú",
        "Iguazú National Park",
        (0.50, 0.50, 1.05),
        "A sweeping video across the curtain of 275 individual cascades that span nearly two miles along the Paraná Plateau."
    ),
    422: (
        "Iguazú Falls Panorama",
        "Iguazú National Park",
        (0.50, 0.50, 1.02),
        "Ultra-wide panorama capturing the full horseshoe sweep of the falls as clouds of spray rise hundreds of feet into the subtropical sky."
    ),
    421: (
        "Into the Devil's Throat",
        "Garganta del Diablo",
        (0.50, 0.50, 1.08),
        "Peering into the roaring mist of Garganta del Diablo, where nearly half of the river's total volume thunders into a single narrow chasm."
    ),
    345: (
        "Rainbow in the Spray",
        "Iguazú Falls",
        (0.50, 0.50, 1.08),
        "Sunlight breaking through the perpetual mist of the lower falls to arc a vivid rainbow across the canyon."
    ),
    334: (
        "Great Dusky Swifts Behind the Falls",
        "Cypseloides senex",
        (0.50, 0.50, 1.10),
        "Great Dusky Swifts clinging to the wet vertical basalt cliffs directly behind the roaring curtain of Iguazú Falls—flying straight through the pounding water to reach their nests!"
    ),
    341: (
        "Great Dusky Swifts on Nest",
        "Cypseloides senex",
        (0.50, 0.50, 1.25),
        "A close-up look at Great Dusky Swifts huddled on their mossy cliffside nest ledge dampened by constant waterfall spray."
    ),
    11: (
        "Here Begins the Pantanal",
        "Transpantaneira Highway",
        (0.50, 0.48, 1.15),
        "The iconic wooden welcome sign marking Kilometer Zero of the Transpantaneira dirt highway—the gateway to the world's largest tropical wetland."
    ),
    56: (
        "Little Woodpecker",
        "Dryobates passerinus",
        (0.47, 0.50, 1.45),
        "True to its name, the Little Woodpecker is a petite, olive-golden woodpecker with a crimson nape and barred underparts that taps quietly along thin upper branches in the Pantanal."
    ),
    131: (
        "Jabiru Nest with Young",
        "Jabiru mycteria",
        (0.45, 0.58, 1.30),
        "A massive treetop stick platform occupied by an adult Jabiru and two downy-gray juveniles. Paired for life, Jabirus return to the same tree crown year after year, adding fresh sticks until the nest can reach nearly ten feet across!"
    ),
    319: (
        "Ultramarine Grosbeak",
        "Cyanoloxia brissonii",
        (0.52, 0.54, 1.85),
        "Framed in a window of cecropia branches, the male Ultramarine Grosbeak gleams in deep midnight-cobalt with shimmering royal-blue shoulder and cheek patches and a massive conical seed-cracking bill."
    ),
    122: (
        "Helmeted Manakin",
        "Antilophia galeata",
        (0.48, 0.48, 1.70),
        "Very out of focus, but we all got great looks at his blazing scarlet crest and forward-curled 'helmet' tuft over the bill—this was the first time our guide had seen a Helmeted Manakin on this trip in many years!"
    ),
    387: (
        "Southern Antpipit",
        "Corythopis delalandi",
        (0.48, 0.48, 1.50),
        "A secretive terrestrial flycatcher of the forest floor that walks like a pipit along fallen branches and leaf litter, flashing a bold black necklace of streaks across its white breast and a bright orange lower mandible."
    ),
    214: (
        "Scarlet-headed Blackbird",
        "Amblyramphus holosericeus",
        (0.55, 0.56, 1.40),
        "Captured right through the eyepiece of our spotting scope! Even across the distant marsh grass, the Scarlet-headed Blackbird's incandescent red-orange hood glows like a beacon against its velvet-black body."
    ),
    134: (
        "Western Cattle-Egret",
        "Bubulcus ibis",
        (0.52, 0.52, 1.15),
        "Perched right atop the back of a white Nelore cow! Originally native to Africa and southern Europe, Cattle Egrets naturally crossed the Atlantic to South America in the late 1800s and spread across the Americas by following grazing livestock to snatch up flushed grasshoppers and ticks."
    ),
    85: (
        "Red-billed Scythebill",
        "Campylorhamphus trochilirostris",
        (0.52, 0.21, 1.30),
        "Hitching up the wooden rafters and probing beneath the terracotta roof tiles of the lodge with its extraordinary, sickle-curved red bill—specialized for reaching spiders and insects tucked deep inside crevices and bamboo stems."
    ),
    243: (
        "Great Potoo",
        "Nyctibius grandis",
        (0.49, 0.45, 1.35),
        "Frozen upright at the end of a rough-barked limb with its eyes shut, the nocturnal Great Potoo looks indistinguishable from a broken gray tree stump—peering through tiny 'magic slits' in its closed eyelids to watch passing intruders without breaking its camouflage."
    ),
    40: (
        "Bare-faced Curassow",
        "Crax fasciolata",
        (0.48, 0.50, 1.25),
        "Strong sexual dimorphism! Unlike the solid black male with his yellow cere, the female Bare-faced Curassow wears intricately barred black-and-white plumage across her back and tail, a warm cinnamon-buff belly, a dark face, and a white-banded curly crest."
    ),
    30: (
        "Ferruginous Pygmy-Owl",
        "Glaucidium brasilianum",
        (0.44, 0.52, 1.45),
        "Turned around to face us with its real, piercing lemon-yellow eyes and bold rufous-and-white streaked breast—despite measuring only six inches tall, the Ferruginous Pygmy-Owl is a fearless daytime ambush hunter."
    ),
    366: (
        "Blue Dacnis",
        "Dacnis cayana",
        (0.48, 0.52, 1.40),
        "In striking contrast to the electric turquoise-and-black male, the female Blue Dacnis is dressed in bright leaf-green plumage with a soft powder-blue crown and cheeks, perched beside a hummingbird feeder at Iguazú."
    ),
    297: (
        "Ferruginous Pygmy-Owl",
        "Glaucidium brasilianum",
        (0.44, 0.45, 1.35),
        "Listen to the rapid, hypnotic series of hollow toots! Despite its tiny size, the Ferruginous Pygmy-Owl's persistent daytime calling carries far through the gallery forest—often drawing in dozens of agitated small songbirds trying to mob it."
    ),
    322: (
        "Tropical Parula",
        "Setophaga pitiayumi",
        (0.43, 0.52, 1.45),
        "Dressed in slate-blue above with a blazing lemon-yellow throat and breast washed in warm orange, this tiny canopy warbler throws back his head to deliver his signature rising, buzzy trill that spills over at the end."
    ),
    268: (
        "Dull-capped Attila",
        "Attila bolivianus",
        (0.58, 0.52, 1.45),
        "Don't let the modest name fool you—perched upright in the shaded understory with its pale iris and warm cinnamon-rufous belly, the Dull-capped Attila belts out a rich, far-carrying series of whistled phrases that echoes across the flooded forest."
    ),
    48: (
        "Smooth-billed Ani",
        "Crotophaga ani",
        (0.58, 0.50, 1.40),
        "A social, coal-black member of the cuckoo family sporting a bizarre, high-arched laterally compressed bill crest and an oversized floppy tail—communal groups even lay their eggs together in a single shared stick nest!"
    ),
}

# Primary tile index -> list of (variant_index, toggle_label)
ALTERNATE_SHOTS = {
    243: [
        (243, "Photo"),
        (409, "Video"),
    ],
    283: [
        (283, "Adult"),
        (210, "Juvenile"),
    ],
    39: [
        (39, "Male"),
        (40, "Female"),
    ],
    30: [
        (30, "Front"),
        (31, "Back (False Eyes)"),
    ],
    367: [
        (367, "Male"),
        (366, "Female"),
    ],
}

# Cloud layout templates: each collage is a list of columns (aligned center vertically & horizontally),
# where outer-left column aligns flex-end, outer-right column aligns flex-start, and inner columns can contain
# single tiles or 2-up horizontal pairs with independent top/bottom heights so ALL 4 outer edges step organically!
GROUPS_SPEC = [
    {
        "id": "jaguars",
        "title": "Jaguars",
        "indices": [169, 164, 159, 142, 171, 189, 160, 168, 173, 188],
        "cloud": [
            {"align": "end", "offsetY": 18, "slots": [(159, 210, 230), (142, 245, 190)]},
            {"align": "end", "offsetY": -14, "slots": [(160, 320, 185), (169, 320, 255), (188, 320, 185)]},
            {"align": "start", "offsetY": 12, "slots": [(164, 295, 200), (173, 295, 190), [(171, 160, 205), (189, 132, 175)]]},
            {"align": "start", "offsetY": -10, "slots": [(168, 240, 185)]}
        ]
    },
    {
        "id": "beautiful",
        "title": "Beautiful",
        "indices": [128, 281, 264, 153, 418, 398, 367],
        "cloud": [
            {"align": "end", "offsetY": 14, "slots": [(264, 215, 245), (398, 250, 195)]},
            {"align": "end", "offsetY": -14, "slots": [(153, 320, 190), (128, 320, 255), (367, 320, 205)]},
            {"align": "start", "offsetY": 10, "slots": [(281, 285, 215), (418, 250, 225)]}
        ]
    },
    {
        "id": "bizarre",
        "title": "...and Bizarre",
        "indices": [243, 277, 104, 175, 5, 132, 113, 206, 39, 48],
        "cloud": [
            {"align": "end", "offsetY": 16, "slots": [(206, 205, 220), (39, 250, 195)]},
            {"align": "end", "offsetY": -18, "slots": [(277, 310, 200), (104, 310, 240), (113, 310, 195)]},
            {"align": "start", "offsetY": 10, "slots": [(243, 290, 225), (48, 290, 190), [(5, 155, 200), (132, 132, 170)]]},
            {"align": "start", "offsetY": -14, "slots": [(175, 235, 210)]}
        ]
    },
    {
        "id": "rare-finds",
        "title": "Rare Finds",
        "indices": [405, 319, 122, 242, 387, 214],
        "cloud": [
            {"align": "end", "offsetY": 14, "slots": [(319, 225, 215)]},
            {"align": "end", "offsetY": -12, "slots": [(242, 320, 195), (405, 320, 240)]},
            {"align": "start", "offsetY": 10, "slots": [[(122, 148, 225), (214, 144, 190)], (387, 295, 215)]}
        ]
    },
    {
        "id": "nests",
        "title": "Nests",
        "indices": [190, 45, 9, 400, 131],
        "cloud": [
            {"align": "end", "offsetY": -10, "slots": [(9, 240, 220)]},
            {"align": "end", "offsetY": 14, "slots": [(45, 325, 200), (131, 325, 235)]},
            {"align": "start", "offsetY": -12, "slots": [(400, 255, 225), (190, 215, 245)]}
        ]
    },
    {
        "id": "bird-calls",
        "title": "Bird Calls",
        "indices": [297, 198, 268, 322],
        "cloud": [
            {"align": "end", "offsetY": 12, "slots": [(297, 255, 220)]},
            {"align": "end", "offsetY": -12, "slots": [(198, 325, 210), (268, 325, 225)]},
            {"align": "start", "offsetY": 10, "slots": [(322, 260, 225)]}
        ]
    },
    {
        "id": "herons",
        "title": "Herons",
        "indices": [13, 20, 212, 187, 283, 97, 92, 95, 134],
        "cloud": [
            {"align": "end", "offsetY": -10, "slots": [(187, 225, 245)]},
            {"align": "end", "offsetY": 15, "slots": [(20, 310, 205), (13, 310, 245), (92, 310, 190)]},
            {"align": "start", "offsetY": -15, "slots": [[(212, 142, 210), (134, 140, 185)], (97, 285, 200), (283, 285, 205)]},
            {"align": "start", "offsetY": 18, "slots": [(95, 205, 255)]}
        ]
    },
    {
        "id": "parrots",
        "title": "Parrots & Macaws",
        "indices": [81, 0, 2, 240, 155, 332, 23, 57, 123, 127],
        "cloud": [
            {"align": "end", "offsetY": 12, "slots": [(2, 200, 210), (57, 245, 190)]},
            {"align": "end", "offsetY": -16, "slots": [(123, 315, 180), (81, 315, 250), (23, 315, 195)]},
            {"align": "start", "offsetY": 14, "slots": [[(240, 145, 200), (332, 147, 170)], (0, 295, 245), (155, 295, 185)]},
            {"align": "start", "offsetY": -8, "slots": [(127, 235, 205)]}
        ]
    },
    {
        "id": "hummingbirds",
        "title": "Hummingbirds",
        "indices": [362, 358, 235, 353, 368, 355, 364, 363, 369, 378],
        "cloud": [
            {"align": "end", "offsetY": -14, "slots": [(235, 215, 195), (364, 250, 205)]},
            {"align": "end", "offsetY": 12, "slots": [(353, 310, 185), (362, 310, 245), (369, 310, 195)]},
            {"align": "start", "offsetY": -12, "slots": [(368, 290, 215), (358, 290, 230), [(355, 145, 195), (378, 142, 165)]]},
            {"align": "start", "offsetY": 16, "slots": [(363, 215, 260)]}
        ]
    },
    {
        "id": "mammals",
        "title": "Mammals",
        "indices": [258, 245, 50, 66, 350, 192, 94, 98, 41, 193],
        "cloud": [
            {"align": "end", "offsetY": 14, "slots": [(66, 210, 195), (41, 255, 205)]},
            {"align": "end", "offsetY": -15, "slots": [(245, 320, 185), (258, 320, 235), (98, 320, 195)]},
            {"align": "start", "offsetY": 10, "slots": [[(350, 148, 235), (193, 144, 205)], (94, 295, 195), (192, 295, 190)]},
            {"align": "start", "offsetY": -12, "slots": [(50, 200, 265)]}
        ]
    },
    {
        "id": "woodpeckers",
        "title": "Woodpeckers",
        "indices": [288, 218, 58, 231, 298, 309, 313, 377, 379, 56],
        "cloud": [
            {"align": "end", "offsetY": -10, "slots": [(58, 205, 205), (231, 245, 195)]},
            {"align": "end", "offsetY": 16, "slots": [(298, 315, 190), (288, 315, 245), (313, 315, 195)]},
            {"align": "start", "offsetY": -14, "slots": [(218, 290, 215), (379, 290, 205), [(309, 142, 200), (377, 145, 170)]]},
            {"align": "start", "offsetY": 12, "slots": [(56, 225, 225)]}
        ]
    },
    {
        "id": "raptors",
        "title": "Raptors & Owls",
        "indices": [121, 14, 12, 136, 135, 224, 140, 213, 30, 292],
        "cloud": [
            {"align": "end", "offsetY": 15, "slots": [(12, 205, 210), (136, 245, 195)]},
            {"align": "end", "offsetY": -12, "slots": [(14, 310, 195), (121, 310, 240), (224, 310, 190)]},
            {"align": "start", "offsetY": 14, "slots": [[(135, 148, 205), (213, 144, 175)], (30, 295, 225), (292, 295, 190)]},
            {"align": "start", "offsetY": -16, "slots": [(140, 235, 200)]}
        ]
    },
    {
        "id": "waterbirds",
        "title": "Waterbirds & Waders",
        "indices": [150, 137, 27, 139, 106, 93, 143, 262, 276],
        "cloud": [
            {"align": "end", "offsetY": -12, "slots": [(137, 210, 205), (93, 250, 195)]},
            {"align": "end", "offsetY": 14, "slots": [(262, 320, 185), (150, 320, 240), (143, 320, 195)]},
            {"align": "start", "offsetY": -14, "slots": [(276, 295, 195), (106, 295, 215), (27, 295, 205)]},
            {"align": "start", "offsetY": 18, "slots": [(139, 215, 230)]}
        ]
    },
    {
        "id": "songbirds",
        "title": "Songbirds & Flycatchers",
        "indices": [85, 84, 312, 232, 75, 54],
        "cloud": [
            {"align": "end", "offsetY": 14, "slots": [(312, 225, 225)]},
            {"align": "end", "offsetY": -12, "slots": [(85, 320, 200), (84, 320, 240)]},
            {"align": "start", "offsetY": 10, "slots": [[(54, 148, 220), (232, 144, 190)], (75, 295, 210)]}
        ]
    },
    {
        "id": "insects-reptiles",
        "title": "Insects & Reptiles",
        "indices": [342, 415, 410, 389, 413, 416, 414, 374, 234, 68],
        "cloud": [
            {"align": "end", "offsetY": -12, "slots": [(410, 200, 230), (416, 245, 190)]},
            {"align": "end", "offsetY": 14, "slots": [(389, 315, 195), (342, 315, 240), (414, 315, 195)]},
            {"align": "start", "offsetY": -16, "slots": [[(415, 142, 215), (68, 150, 180)], (234, 295, 205), (374, 295, 190)]},
            {"align": "start", "offsetY": 10, "slots": [(413, 195, 255)]}
        ]
    },
    {
        "id": "iguazu",
        "title": "Iguazú Falls",
        "indices": [420, 419, 422, 421, 345, 334, 341],
        "cloud": [
            {"align": "end", "offsetY": 12, "slots": [(341, 245, 215)]},
            {"align": "end", "offsetY": -14, "slots": [(422, 340, 175), (420, 340, 235), (345, 340, 200)]},
            {"align": "start", "offsetY": 10, "slots": [(419, 305, 195), (421, 305, 220), (334, 235, 185)]}
        ]
    }
]

def create_cropped_tile(idx, target_w, target_h, focus):
    src_path = f"/home/antigravity/fortenforge/pantanal/media/photos/item_{idx:03d}.jpg"
    out_path = f"/home/antigravity/fortenforge/pantanal/media/crops/item_{idx:03d}.jpg"
    cx, cy, zoom = focus
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        iw, ih = im.size
        target_ratio = target_w / target_h
        img_ratio = iw / ih

        # First compute largest box of target_ratio inside (iw, ih)
        if img_ratio > target_ratio:
            base_h = ih
            base_w = ih * target_ratio
        else:
            base_w = iw
            base_h = iw / target_ratio

        # Apply zoom factor
        crop_w = base_w / max(zoom, 1.0)
        crop_h = base_h / max(zoom, 1.0)

        # Center around (cx * iw, cy * ih), clamped to image bounds
        left = cx * iw - crop_w / 2
        top = cy * ih - crop_h / 2
        left = max(0, min(iw - crop_w, left))
        top = max(0, min(ih - crop_h, top))

        cropped = im.crop((int(left), int(top), int(left + crop_w), int(top + crop_h)))
        # Resize to 2x display resolution for crisp Retina rendering while keeping file size ~40KB
        out_w = int(target_w * 2)
        out_h = int(target_h * 2)
        resized = cropped.resize((out_w, out_h), Image.Resampling.LANCZOS)
        resized.save(out_path, "JPEG", quality=84, optimize=True)

output_groups = []
for g in GROUPS_SPEC:
    items_dict = {}
    # Extract tile dimensions from cloud slots
    dims_by_idx = {}
    for col in g["cloud"]:
        for slot in col["slots"]:
            if isinstance(slot, list):
                for sub_idx, w, h in slot:
                    dims_by_idx[sub_idx] = (w, h)
            else:
                s_idx, w, h = slot
                dims_by_idx[s_idx] = (w, h)

    for idx in g["indices"]:
        raw = catalog[idx]
        species, sci, focus, human_caption = ANNOTATIONS[idx]
        tw, th = dims_by_idx[idx]
        create_cropped_tile(idx, tw, th, focus)

        dt = datetime.datetime.utcfromtimestamp(raw["timestamp"] / 1000)
        date_str = dt.strftime("%b %d, %Y")
        region = "Pantanal, Brazil" if (idx <= 298 or idx == 409) else "Iguazú Falls"
        dur_s = round(raw["video_duration_ms"] / 1000) if raw["is_video"] and raw["video_duration_ms"] else None
        variants = None
        if idx in ALTERNATE_SHOTS:
            variants = []
            for v_idx, v_label in ALTERNATE_SHOTS[idx]:
                v_raw = catalog[v_idx]
                v_species, _, _, v_caption = ANNOTATIONS[v_idx]
                v_dt = datetime.datetime.utcfromtimestamp(v_raw["timestamp"] / 1000)
                v_date_str = v_dt.strftime("%b %d, %Y")
                v_region = "Pantanal, Brazil" if (v_idx <= 298 or v_idx == 409) else "Iguazú Falls"
                variants.append({
                    "index": v_idx,
                    "label": v_label,
                    "id": v_raw["id"],
                    "species": v_species,
                    "caption": v_caption,
                    "isVideo": v_raw["is_video"],
                    "photoUrl": f"media/photos/item_{v_idx:03d}.jpg",
                    "videoUrl": f"media/videos/item_{v_idx:03d}.mp4" if v_raw["is_video"] else None,
                    "date": v_date_str,
                    "region": v_region,
                })

        items_dict[idx] = {
            "index": idx,
            "id": raw["id"],
            "species": species,
            "caption": human_caption,
            "originalNote": raw["caption"],
            "isVideo": raw["is_video"],
            "durationSec": dur_s,
            "tileWidth": tw,
            "tileHeight": th,
            "cropUrl": f"media/crops/item_{idx:03d}.jpg",
            "photoUrl": f"media/photos/item_{idx:03d}.jpg",
            "videoUrl": f"media/videos/item_{idx:03d}.mp4" if raw["is_video"] else None,
            "date": date_str,
            "region": region,
            "filename": raw["filename"],
            "variants": variants,
        }

    # Build cloud columns structure with hydrated item objects
    cloud_cols = []
    for col in g["cloud"]:
        hydrated_slots = []
        for slot in col["slots"]:
            if isinstance(slot, list):
                hydrated_slots.append({
                    "type": "pair",
                    "items": [items_dict[sub_idx] for sub_idx, _, _ in slot]
                })
            else:
                s_idx, _, _ = slot
                hydrated_slots.append({
                    "type": "single",
                    "item": items_dict[s_idx]
                })
        cloud_cols.append({
            "align": col["align"],
            "offsetY": col["offsetY"],
            "slots": hydrated_slots
        })

    output_groups.append({
        "id": g["id"],
        "title": g["title"],
        "items": [items_dict[idx] for idx in g["indices"]],
        "cloud": cloud_cols
    })

import hashlib, re

json_str = json.dumps({"groups": output_groups}, indent=2, ensure_ascii=False)
version_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()[:8]

# Append cache-busting query param to cropUrls so updated crops never serve stale from browser cache
for g in output_groups:
    for item in g["items"]:
        item["cropUrl"] = f"{item['cropUrl']}?v={version_hash}"

with open("/home/antigravity/fortenforge/pantanal/data/wildlife_data.json", "w", encoding="utf-8") as f:
    json.dump({"groups": output_groups}, f, indent=2, ensure_ascii=False)

with open("/home/antigravity/fortenforge/pantanal/data/wildlife_data.js", "w", encoding="utf-8") as f:
    f.write("window.WILDLIFE_DATA = ")
    json.dump({"groups": output_groups}, f, indent=2, ensure_ascii=False)
    f.write(";\n")

# Stamp version_hash into index.html for index.css, data/wildlife_data.js, and app.js
index_html_path = "/home/antigravity/fortenforge/pantanal/index.html"
with open(index_html_path, "r", encoding="utf-8") as f:
    html = f.read()
html = re.sub(r'href="index\.css(\?v=[^"]*)?"', f'href="index.css?v={version_hash}"', html)
html = re.sub(r'src="data/wildlife_data\.js(\?v=[^"]*)?"', f'src="data/wildlife_data.js?v={version_hash}"', html)
html = re.sub(r'src="app\.js(\?v=[^"]*)?"', f'src="app.js?v={version_hash}"', html)
with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built {len(output_groups)} photo-cloud collages with {sum(len(g['items']) for g in output_groups)} custom-cropped tiles! (v={version_hash})")
