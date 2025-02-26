import glob
import datetime
import configparser
import ast
from moviepy import (
	VideoFileClip,
	TextClip,
	CompositeVideoClip,
	concatenate_videoclips,
	vfx
)

# iniファイルの読み込み
conf_ini = configparser.ConfigParser()
conf_ini.read('./setting.ini', encoding = 'utf-8')

# iniファイルの設定値をラッチ
output_file		= conf_ini['GENERAL']['FileName']
font			= conf_ini['TEXT']['Font']
text_color		= ast.literal_eval(conf_ini['TEXT']['TextColor'])
stroke_color	= ast.literal_eval(conf_ini['TEXT']['StrokeColor'])
bg_color		= ast.literal_eval(conf_ini['TEXT']['BgColor'])
stroke_width	= int(conf_ini['TEXT']['StrokeWidth'])
width			= int(conf_ini['ENCODE']['Width'])
height			= int(conf_ini['ENCODE']['Height'])
nvenc			= conf_ini['ENCODE']['Nvenc']

# 現在時刻を取得
t_delta = datetime.timedelta(hours = 9)
JST = datetime.timezone(t_delta, 'JST')
date = datetime.datetime.now(JST).strftime('%Y%m%d%H%M%S')

# 入力ファイルの取得
input_files = glob.glob("./input/*.mp4")

# 出力ファイル名の設定
if (output_file == 'default'):
	output_file = "./output/combined_video_" + date + ".mp4"

# 編集開始
input_clips = []
for file in input_files:
	clip = VideoFileClip(file)								# 動画ファイルから動画クリップに変換
	if (clip.w != width) or (clip.h != height):				# サイズの調整
		clip = clip.with_effects([vfx.Resize((width, height))])

	# テロップ用の文字列を取り出す
	title = file
	title = title.replace('./input\\', '')
	title = title.replace('.mp4', '')

	time = clip.duration # 動画時間の取得

	# テキストクリップ作成
	text_clip = TextClip(
		font = font,
		text = title,
		font_size = 70,
		color = text_color,
		bg_color = bg_color,
		stroke_color = stroke_color,
		stroke_width = stroke_width,
		duration = time,
		margin = (3, 3, 0, 0),
		transparent = True,
	)

	# テキストクリップと動画クリップを合わせる
	clip = CompositeVideoClip([clip, text_clip])

	input_clips.append(clip)	# 配列に格納

# 最終的に書き出すClipに動画を結合する
output_clip = concatenate_videoclips(input_clips)

# 動画の書き出し
if (nvenc == 'true'):
	print('### Encode with Hardware Encode(H.264) ###')
	output_clip.write_videofile(output_file, codec = 'h264_nvenc')
else:
	print('### Encode with Software Encode ###')
	output_clip.write_videofile(output_file)
