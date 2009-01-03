#!/bin/zsh

program_name=$(basename $0)

show_help() {
	echo "
0. Blues		42. Soul		84. Fast Fusion
1. Classic Rock		43. Punk		85. Bebob
2. Country		44. Space		86. Latin
3. Dance		45. Meditative		87. Revival
4. Disco		46. Instrumental Pop	88. Celtic
5. Funk			47. Instrumental Rock	89. Bluegrass
6. Grunge		48. Ethnic		90. Avantgarde
7. Hip-Hop		49. Gothic		91. Gothic Rock
8. Jazz			50. Darkwave		92. Progressive Rock
9. Metal		51. Techno-Industrial	93. Psychedelic Rock
10. New Age		52. Electronic		94. Symphonic Rock
11. Oldies		53. Pop-Folk		95. Slow Rock
12. Other		54. Eurodance		96. Big Band
13. Pop			55. Dream		97. Chorus
14. R&B			56. Southern Rock	98. Easy Listening
15. Rap			57. Comedy		99. Acoustic
16. Reggae		58. Cult		100. Humour
17. Rock		59. Gangsta		101. Speech
18. Techno		60. Top 40		102. Chanson
19. Industrial		61. Christian Rap	103. Opera
20. Alternative		62. Pop/Funk		104. Chamber Music
21. Ska			63. Jungle		105. Sonata
22. Death Metal		64. Native American	106. Symphony
23. Pranks		65. Cabaret		107. Booty Bass
24. Soundtrack		66. New Wave		108. Primus
25. Euro-Techno		67. Psychadelic		109. Porn Groove
26. Ambient		68. Rave		110. Satire
27. Trip-Hop		69. Showtunes		111. Slow Jam
28. Vocal		70. Trailer		112. Club
29. Jazz+Funk		71. Lo-Fi		113. Tango
30. Fusion		72. Tribal		114. Samba
31. Trance		73. Acid Punk		115. Folklore
32. Classical		74. Acid Jazz		116. Ballad
33. Instrumental	75. Polka		117. Power Ballad
34. Acid		76. Retro		118. Rhythmic Soul
35. House		77. Musical		119. Freestyle
36. Game		78. Rock & Roll		120. Duet
37. Sound Clip		79. Hard Rock		121. Punk Rock
38. Gospel		80. Folk		122. Drum Solo
39. Noise		81. Folk-Rock		123. A capella
40. AlternRock		82. National Folk	124. Euro-House
41. Bass		83. Swing		125. Dance Hall
	"
}

show_invalid_usage() {
	echo "$program_name: too few arguments
	Try '$program_name <number of files> <genre code>'"
}

# handle command line arguments
while [[ $1 == -* ]]; do
    case "$1" in
        -h|--help) show_help; exit 0;;
    esac
done

# check there is least two arguments
if [ ! "$#@" -ge 2 ]; then
	show_invalid_usage
	exit
fi

for i in {1..$@[1]}; do;
	num=$RANDOM && 
	cp input.mp3 $num.mp3 && 
	id3v2 -a "An Artist" -A "An album" -t "Song $num" -g $@[2] $num.mp3; 
done
