from PyQt5.QtCore import QTimer

class AnimationController:
    """Controls animation timing and states"""
    
    def __init__(self, interval=250, callback=None):
        self.interval = interval
        self.callback = callback
        self.anim_state = 0
        self.enabled = True
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(interval)
    
    def _update_animation(self):
        """Update animation state and call callback"""
        if self.enabled:
            self.anim_state = (self.anim_state + 1) % 4
            if self.callback:
                self.callback(self.anim_state)
    
    def set_enabled(self, enabled):
        """Enable or disable animations"""
        self.enabled = enabled
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
            self.anim_state = 0
            if self.callback:
                self.callback(self.anim_state)
    
    def is_enabled(self):
        """Check if animations are enabled"""
        return self.enabled
    
    def get_state(self):
        """Get current animation state (0-3)"""
        return self.anim_state
