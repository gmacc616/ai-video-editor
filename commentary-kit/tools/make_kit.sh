#!/usr/bin/env bash
# Generates the license-free commentary SFX + overlay kit with ffmpeg only.
# Usage: bash make_kit.sh   (run from anywhere; writes next to this script's parent)
set -e
KIT="$(cd "$(dirname "$0")/.." && pwd)"
S="$KIT/sfx/generated"; O="$KIT/overlays"; T="$KIT/transitions"
mkdir -p "$S" "$O" "$T"
ff() { ffmpeg -hide_banner -loglevel error -y "$@"; }
A="-ar 48000 -ac 2 -c:a pcm_s16le"

# --- SFX (48 kHz WAV) ---
ff -f lavfi -i "aevalsrc='0.9*sin(2*PI*(38+110*exp(-9*t))*t)*exp(-2.6*t)':d=1.6" -af "alimiter=limit=0.95" $A "$S/boom_impact.wav"
ff -f lavfi -i "aevalsrc='0.9*sin(2*PI*(30+60*exp(-5*t))*t)*exp(-1.4*t)':d=3" -af "lowpass=f=180,alimiter=limit=0.95" $A "$S/boom_deep_sub.wav"
ff -f lavfi -i "anoisesrc=d=0.55:c=pink:a=0.9" -af "bandpass=f=1200:width_type=h:w=1500,volume='pow(sin(PI*t/0.55),3)':eval=frame,afade=t=out:st=0.45:d=0.1" $A "$S/whoosh_short.wav"
ff -f lavfi -i "anoisesrc=d=1.1:c=pink:a=0.9" -af "bandpass=f=700:width_type=h:w=1000,volume='pow(sin(PI*t/1.1),2)':eval=frame" $A "$S/whoosh_long.wav"
ff -f lavfi -i "anoisesrc=d=2.2:c=white:a=0.5" -f lavfi -i "aevalsrc='0.3*sin(2*PI*(200*t+300*t*t))':d=2.2" -filter_complex "[0]highpass=f=800,volume='t/2.2':eval=frame[n];[1]volume='t/2.2':eval=frame[s];[n][s]amix=inputs=2,afade=t=out:st=2.1:d=0.1" $A "$S/riser_2s.wav"
ff -f lavfi -i "sine=f=1000:d=0.6" -af "volume=6,afade=t=in:d=0.005,afade=t=out:st=0.59:d=0.01" $A "$S/censor_bleep.wav"
ff -f lavfi -i "aevalsrc='0.8*sin(2*PI*(900*exp(-30*t)+200)*t)*exp(-25*t)':d=0.15" $A "$S/pop.wav"
ff -f lavfi -i "aevalsrc='0.4*(sin(2*PI*1760*t)+0.5*sin(2*PI*3520*t)+0.25*sin(2*PI*5280*t))*exp(-4*t)':d=1.5" $A "$S/ding.wav"
ff -f lavfi -i "aevalsrc='0.35*sgn(sin(2*PI*140*t))*(lt(t,0.18)+between(t,0.25,0.55))':d=0.6" -af "lowpass=f=2500" $A "$S/wrong_buzzer.wav"
ff -f lavfi -i "aevalsrc='0.35*(sin(2*PI*1046*t)*lt(t,0.12)+sin(2*PI*1568*t)*between(t,0.12,0.5)*exp(-5*(t-0.12)))':d=0.5" $A "$S/correct_chime.wav"
ff -f lavfi -i "anoisesrc=d=0.25:c=white:a=0.9" -af "highpass=f=1500,volume='exp(-30*t)':eval=frame" $A "$S/camera_shutter.wav"
ff -f lavfi -i "anoisesrc=d=0.6:c=white:a=0.7" -af "acrusher=bits=4:mode=log:aa=1:samples=20,volume='0.5+0.5*sgn(sin(2*PI*14*t))':eval=frame" $A "$S/glitch_burst.wav"
ff -f lavfi -i "aevalsrc='0.6*sin(2*PI*2000*t)*exp(-60*mod(t,0.5))':d=4" -af "highpass=f=800" $A "$S/clock_tick_4s.wav"
ff -f lavfi -i "aevalsrc='0.25*(sin(2*PI*55*t)+0.6*sin(2*PI*82.4*t)+0.3*sin(2*PI*110.5*t))*(0.7+0.3*sin(2*PI*0.25*t))':d=12" -af "lowpass=f=400,afade=t=in:d=2,afade=t=out:st=10:d=2" $A "$S/suspense_drone_12s.wav"
ff -f lavfi -i "aevalsrc='0.5*sin(2*PI*(600-500*t/0.8)*t)*exp(-1.5*t)':d=0.8" $A "$S/slide_down_fail.wav"
ff -f lavfi -i "anoisesrc=d=0.08:c=white:a=0.8" -af "bandpass=f=3000:width_type=h:w=3000,volume='exp(-50*t)':eval=frame" $A "$S/click.wav"
ff -f lavfi -i "aevalsrc='0.9*sin(2*PI*(60+40*exp(-12*t))*t)*exp(-6*t)':d=0.5" -f lavfi -i "anoisesrc=d=0.5:c=white:a=0.6" -filter_complex "[1]highpass=f=3000,volume='exp(-40*t)':eval=frame[n];[0][n]amix=inputs=2:normalize=0,alimiter=limit=0.95" $A "$S/punch_hit.wav"
ff -f lavfi -i "aevalsrc='0.4*sin(2*PI*(400+1200*t)*t)*(1-t/0.4)':d=0.4" $A "$S/zoom_in_blip.wav"

# --- Overlays (1920x1080, 30 fps) ---
ff -f lavfi -i "color=c=gray:s=1280x720:r=30:d=4" -vf "noise=alls=30:allf=t+u,format=gray,format=yuv420p" -c:v libx264 -crf 30 "$O/film_grain_4s_overlay-blend.mp4"
ff -f lavfi -i "color=c=black:s=1920x1080:r=30:d=6" -vf "noise=alls=60:allf=t+u,geq=lum='lum(X,Y)*0.35+40*lt(mod(Y,4),2)':cb=128:cr=128,eq=contrast=1.2,format=yuv420p" -c:v libx264 -crf 22 "$O/vhs_scanlines_6s_screen-blend.mp4"
ff -f lavfi -i "color=c=black@0:s=1920x1080,format=rgba" -frames:v 1 -vf "geq=r=0:g=0:b=0:a='255*min(1,pow(hypot(X-W/2,Y-H/2)/hypot(W/2,H/2),2)*1.4)'" "$O/vignette.png"
ff -f lavfi -i "color=c=black@0:s=600x600,format=rgba" -frames:v 1 -vf "geq=r=230:g=20:b=20:a='255*between(hypot(X-300,Y-300),255,285)'" "$O/red_circle_highlight.png"
ff -f lavfi -i "color=c=black@0:s=900x300,format=rgba" -frames:v 1 -vf "geq=r=230:g=20:b=20:a='255*(between(X,20,640)*between(Y,125,175)+between(X,600,880)*lt(abs(Y-150),(880-X)*0.5)*gte(X,600))'" "$O/red_arrow_right.png"
ff -f lavfi -i "color=c=black@0:s=1920x1080,format=rgba" -frames:v 1 -vf "geq=r=0:g=0:b=0:a='255*(lt(Y,130)+gt(Y,950))'" "$O/letterbox_bars.png"

# --- Transition plates ---
ff -f lavfi -i "color=c=white:s=1920x1080:r=30:d=0.4" -vf "fade=t=in:d=0.08,fade=t=out:st=0.12:d=0.28,format=yuv420p" -c:v libx264 -crf 18 "$T/white_flash_0.4s_screen-blend.mp4"
ff -f lavfi -i "color=c=black:s=1920x1080:r=30:d=0.5" -f lavfi -i "anoisesrc=d=0.5:c=white:a=0.6" -filter_complex "[0]noise=alls=100:allf=t,rgbashift=rh=-30:bh=30,format=yuv420p[v]" -map "[v]" -map 1 -c:v libx264 -crf 28 -c:a aac -shortest "$T/static_glitch_0.5s.mp4"
echo "Kit written to $KIT"

# Peak-normalise every SFX to -1 dBFS so they sit at a consistent starting level
for f in "$S"/*.wav; do
  pk=$(ffmpeg -hide_banner -i "$f" -af volumedetect -f null - 2>&1 | sed -n 's/.*max_volume: \(-*[0-9.]*\) dB/\1/p')
  g=$(awk -v p="$pk" 'BEGIN{print -1 - p}')
  ff -i "$f" -af "volume=${g}dB" $A "$f.tmp.wav" && mv -f "$f.tmp.wav" "$f"
done
