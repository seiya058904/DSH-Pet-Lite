"""Core-only, frame-driven roaming; no additional timers or background work.

Uses v4.4.0's calibrated stride curves. The absent random category becomes idle.
One complete stride per move, bounded to the current work area.
"""
import json


class Roaming:
    def __init__(self, pet):
        self.pet = pet
        self.strides = json.loads((pet.assets / 'move_strides.json').read_text(encoding='utf-8'))
        self.facing = -1
        self.pending = None
        self.plan = None
        self.flip_after_turn = False
        self.groups = {}
        for name, clip in pet.manifest['clips'].items():
            self.groups.setdefault(clip['category'], []).append(name)

    def prepare(self, name):
        p = self.pet
        self.plan = None
        self.pending = None
        self.flip_after_turn = False
        category = p.manifest['clips'][name]['category']
        if category == 'turn':
            self.flip_after_turn = True
        elif category == 'move':
            g = p.screen().availableGeometry()
            stride = self.strides[p.manifest['clips'][name]['label']]['stride'] * p.manifest['scale']
            left, right = p.x() - g.left(), g.right() + 1 - p.width() - p.x()
            direction = self.facing
            if (left if direction < 0 else right) < stride:
                direction = -direction
            room = max(0, left if direction < 0 else right)
            if direction != self.facing:
                self.pending = name
                self.flip_after_turn = True
                return self.groups['turn'][0]
            self.plan = (p.x(), direction * min(stride, room))
        return name

    def completed(self, name):
        if self.flip_after_turn:
            self.facing *= -1
            self.flip_after_turn = False
        if self.pending:
            name, self.pending = self.pending, None
            return self.prepare(name)
        if name != 'idle':
            return self.prepare('idle')
        category = self.pet.rng.choices(['idle', 'turn', 'move'], [70, 10, 20])[0]
        return self.prepare(self.pet.rng.choice(self.groups[category]))

    def advance(self):
        if self.plan is None or self.pet.drag_origin is not None:
            return
        p = self.pet
        curve = self.strides[p.manifest['clips'][p.clip]['label']]['curve']
        progress = curve[min(p.index, len(curve)-1)]
        g = p.screen().availableGeometry()
        x = round(self.plan[0] + self.plan[1] * progress)
        p.move(max(g.left(), min(x, g.right()+1-p.width())), p.y())
