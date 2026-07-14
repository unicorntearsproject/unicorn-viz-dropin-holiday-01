"""America 250 - over-the-top bicentennial-plus-50 celebration effect.

Procedural patriotic spectacle for the America 250 anniversary: flowing flag
ribbons, star fields, refractive fireworks, beat flashes, and glowing 250
numerals.  Audio energy drives fireworks scale, ribbon motion, spark density,
and camera pulse.
"""
from __future__ import annotations

__version__ = '0.5.0'

import moderngl

from unicornviz.effects.base import AudioData, BaseEffect

_VERT = """
#version 330
in vec2 in_vert;
out vec2 v_uv;
void main() {
    v_uv = in_vert * 0.5 + 0.5;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

_FRAG = """
#version 330
// Fragment shader - procedural America 250 scene.
// Uniforms: time/resolution/audio controls/style seed.
// Produces: full-screen patriotic ribbons, fireworks, stars, and 250 numerals.
uniform float iTime;
uniform vec2  iResolution;
uniform float iBass;
uniform float iMid;
uniform float iTreble;
uniform float iBeat;
uniform float iSpeed;
uniform float iZoom;
uniform float iReactivity;
uniform float iGlow;
uniform float iSeed;
in vec2 v_uv;
out vec4 fragColor;

#define TAU 6.28318530

float hash(vec2 p) {
    p = fract(p * vec2(127.1, 311.7));
    p += dot(p, p + 19.19);
    return fract(p.x * p.y);
}

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float sevenSeg(vec2 p, int digit) {
    float a = 0.0;
    float w = 0.055;
    bool top = false; bool ul = false; bool ur = false;
    bool mid = false; bool ll = false; bool lr = false; bool bot = false;
    if (digit == 0) { top=true; ul=true; ur=true; ll=true; lr=true; bot=true; }
    if (digit == 2) { top=true; ur=true; mid=true; ll=true; bot=true; }
    if (digit == 5) { top=true; ul=true; mid=true; lr=true; bot=true; }
    if (top) a = max(a, smoothstep(w, 0.0, sdBox(p - vec2(0.0, 0.34), vec2(0.24, w))));
    if (mid) a = max(a, smoothstep(w, 0.0, sdBox(p, vec2(0.24, w))));
    if (bot) a = max(a, smoothstep(w, 0.0, sdBox(p + vec2(0.0, 0.34), vec2(0.24, w))));
    if (ul) a = max(a, smoothstep(w, 0.0, sdBox(p - vec2(-0.25, 0.17), vec2(w, 0.18))));
    if (ur) a = max(a, smoothstep(w, 0.0, sdBox(p - vec2( 0.25, 0.17), vec2(w, 0.18))));
    if (ll) a = max(a, smoothstep(w, 0.0, sdBox(p - vec2(-0.25,-0.17), vec2(w, 0.18))));
    if (lr) a = max(a, smoothstep(w, 0.0, sdBox(p - vec2( 0.25,-0.17), vec2(w, 0.18))));
    return a;
}

float starShape(vec2 p, float r) {
    float a = atan(p.y, p.x);
    float d = length(p);
    float spikes = 0.72 + 0.28 * cos(a * 5.0);
    return smoothstep(r, r * 0.35, d * spikes);
}

vec3 fireworks(vec2 uv, float t, float react) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 14; i++) {
        float fi = float(i);
        vec2 center = vec2(hash(vec2(fi, iSeed)) * 2.0 - 1.0,
                           hash(vec2(fi + 9.1, iSeed)) * 1.25 - 0.08);
        float phase = fract(t * (0.08 + 0.018 * hash(vec2(fi, 4.0))) + hash(vec2(fi, 8.0)));
        float radius = phase * (0.18 + hash(vec2(fi, 6.0)) * 0.48) * (0.85 + iBass * react * 0.45);
        float life = sin(phase * 3.14159);
        float d = length(uv - center);
        float ring = smoothstep(0.020, 0.0, abs(d - radius));
        float rays = pow(max(0.0, cos(atan(uv.y-center.y, uv.x-center.x) * (10.0 + mod(fi, 6.0)) + fi)), 18.0);
        vec3 tint = 0.55 + 0.45 * cos(TAU * (vec3(0.0, 0.33, 0.67) + fi * 0.13 + iSeed));
        col += tint * ring * rays * life * (0.55 + iTreble * react);
    }
    return col;
}

void main() {
    float t = iTime * max(iSpeed, 0.05);
    float react = max(iReactivity, 0.1);
    vec2 uv = (v_uv * 2.0 - 1.0) * vec2(iResolution.x / max(iResolution.y, 1.0), 1.0);
    uv /= max(iZoom, 0.1) * (1.0 + iBeat * 0.025);

    vec3 navy = vec3(0.010, 0.022, 0.095);
    vec3 red = vec3(0.87, 0.028, 0.060);
    vec3 white = vec3(0.86, 0.84, 0.75);
    vec3 blue = vec3(0.030, 0.120, 0.49);
    vec3 gold = vec3(1.0, 0.63, 0.11);

    vec3 col = navy * (0.78 + iBass * 0.23);

    // Flowing flag ribbons across the whole sky.
    float wave = sin(uv.x * 2.8 + t * 0.8 + sin(uv.y * 4.0 + t * 0.35) * 1.4);
    float stripe_coord = (uv.y + wave * 0.10 + t * 0.04 + iMid * 0.10) * 7.5;
    float stripe = step(0.5, fract(stripe_coord));
    float ribbon = smoothstep(1.05, -0.18, abs(uv.y + wave * 0.05));
    vec3 stripe_col = mix(red * 0.75, white * 0.68, stripe);
    col = mix(col, stripe_col, ribbon * (0.19 + iGlow * 0.090));

    // Blue canton-like energy field with procedural stars.
    vec2 canton = uv - vec2(-0.62, 0.34);
    float canton_mask = smoothstep(0.50, 0.47, abs(canton.x)) * smoothstep(0.36, 0.33, abs(canton.y));
    col = mix(col, blue * (0.80 + iMid * 0.18), canton_mask * 0.58);
    vec2 grid = fract((canton + vec2(0.5, 0.35)) * vec2(7.0, 5.0)) - 0.5;
    float st = starShape(grid, 0.15) * canton_mask;
    col += white * st * (0.30 + iTreble * 0.50);

    // Fireworks and sparkle sky.
    col += fireworks(uv, t, react) * (0.67 + iGlow * 0.22);
    vec2 cell = floor((uv + vec2(1.8, 1.0)) * vec2(48.0, 28.0));
    vec2 local = fract((uv + vec2(1.8, 1.0)) * vec2(48.0, 28.0)) - 0.5;
    float sparkle = step(0.992 - iTreble * 0.006, hash(cell + floor(t * 3.0)));
    col += white * sparkle * exp(-dot(local, local) * 26.0) * (0.16 + iTreble * 0.66);

    // Monumental 250 numerals.
    vec2 p = uv;
    p.y += 0.08 + sin(t * 0.7) * 0.015;
    float d2 = sevenSeg((p - vec2(-0.42, -0.14)) / 0.58, 2);
    float d5 = sevenSeg((p - vec2( 0.00, -0.14)) / 0.58, 5);
    float d0 = sevenSeg((p - vec2( 0.42, -0.14)) / 0.58, 0);
    float nums = max(max(d2, d5), d0);
    float num_glow = smoothstep(0.62, 0.0, length(vec2(p.x * 0.85, p.y + 0.14)));
    vec2 num_cell = floor((p + vec2(1.2, 0.72)) * vec2(62.0, 34.0));
    vec2 num_local = fract((p + vec2(1.2, 0.72)) * vec2(62.0, 34.0)) - 0.5;
    float inner_wave = 0.5 + 0.5 * sin(p.x * 24.0 - p.y * 18.0 + t * 4.8 + iSeed * TAU);
    float inner_ribbon = smoothstep(0.07, 0.0, abs(fract(p.x * 4.5 + p.y * 3.2 - t * 0.85) - 0.5));
    float inner_spark = step(0.974 - iTreble * 0.012, hash(num_cell + floor(t * 9.0)))
        * exp(-dot(num_local, num_local) * 68.0);
    float d2_outer = sevenSeg((p - vec2(-0.42, -0.14)) / 0.62, 2);
    float d5_outer = sevenSeg((p - vec2( 0.00, -0.14)) / 0.62, 5);
    float d0_outer = sevenSeg((p - vec2( 0.42, -0.14)) / 0.62, 0);
    float rim = max(max(max(d2_outer, d5_outer), d0_outer) - nums, 0.0);
    vec3 num_core = mix(gold * 0.72, vec3(1.0, 0.92, 0.38), inner_wave);
    num_core += mix(red, blue, 0.5 + 0.5 * sin(t * 1.7 + p.x * 5.0)) * inner_ribbon * 0.38;
    col += num_core * nums * (0.78 + iBeat * 0.62 + iGlow * 0.26);
    col += vec3(1.0, 0.95, 0.55) * inner_spark * nums * (0.90 + iTreble * 1.00);
    col += vec3(1.0, 0.82, 0.18) * rim * (0.65 + iBeat * 0.72);
    col += mix(red, blue, 0.45 + 0.35 * sin(t)) * num_glow * nums * 0.24;

    // Eagle-wing-ish light arcs, abstract and celebratory.
    float wingL = smoothstep(0.035, 0.0, abs(length((uv - vec2(-0.42, -0.02)) * vec2(1.0, 2.8)) - 0.55));
    float wingR = smoothstep(0.035, 0.0, abs(length((uv - vec2( 0.42, -0.02)) * vec2(1.0, 2.8)) - 0.55));
    col += vec3(0.40, 0.68, 1.0) * (wingL + wingR) * (0.10 + iMid * react * 0.20);

    // Beat bloom and vignette.
    col += vec3(1.0, 0.80, 0.38) * iBeat * 0.21;
    float vig = 1.0 - dot(v_uv - 0.5, v_uv - 0.5) * 0.93;
    col *= vig;
    col = col / (col + 1.00);
    col = pow(clamp(col, 0.0, 1.0), vec3(0.97));
    col = clamp((col - 0.40) * 1.20 + 0.40, 0.0, 1.0);

    fragColor = vec4(col, 1.0);
}
"""


class America250(BaseEffect):
    """Procedural America 250 celebration with fireworks and flag ribbons."""

    NAME = 'America 250'
    AUTHOR = 'unicorn-viz drop-in'
    TAGS = ['holiday', 'america', 'patriotic', 'fireworks', 'energetic']
    PING_PONG_FRIENDS = ['Disco Ball', 'Grand Finale', 'Fireworks', 'Starfield']

    def _init(self) -> None:
        self.parameters = {
            'speed': float(self.config.get('speed', 1.0)),
            'zoom': float(self.config.get('zoom', 1.0)),
            'reactivity': float(self.config.get('reactivity', 1.15)),
            'glow': float(self.config.get('glow', 1.25)),
        }
        self._prog = self._make_program(_VERT, _FRAG)
        self._vao, self._vbo = self._fullscreen_quad(self._prog)
        self._seed = float(self.rng.uniform(0.0, 1.0))
        self._bass = 0.0
        self._mid = 0.0
        self._treble = 0.0
        self._beat = 0.0

    def update(self, dt: float, audio: AudioData) -> None:
        super().update(dt, audio)
        self._bass = float(audio.bass_n)
        self._mid = float(audio.mid_n)
        self._treble = float(audio.treble_n)
        if audio.beat > 0.5:
            self._beat = 1.0
        self._beat = max(0.0, self._beat - dt * 3.4)

    def _set(self, name: str, value) -> None:
        try:
            self._prog[name].value = value
        except KeyError:
            pass

    def render(self) -> None:
        self._set('iTime', self.time)
        self._set('iResolution', (float(self.width), float(self.height)))
        self._set('iBass', self._bass)
        self._set('iMid', self._mid)
        self._set('iTreble', self._treble)
        self._set('iBeat', self._beat)
        self._set('iSpeed', float(self.parameters['speed']))
        self._set('iZoom', float(self.parameters['zoom']))
        self._set('iReactivity', float(self.parameters['reactivity']))
        self._set('iGlow', float(self.parameters['glow']))
        self._set('iSeed', self._seed)
        self._vao.render(moderngl.TRIANGLE_STRIP)

    def destroy(self) -> None:
        self._vao.release()
        self._vbo.release()
        self._prog.release()
