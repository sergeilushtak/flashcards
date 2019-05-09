
class interval ():
    def __init__ (self, start, size):
        self.start = start
        self.size = size

class FloatingWindow ():

    class state ():
        def __init__ (self, new, prev, window):

                self.new = new
                self.prev = prev
                self.window = window
    """

    def __init__ (self, settings, entry_count, suggested_index):

        self.stateL = []

        if  entry_count > 0:

            def fit_in_frame (pos):
                pos = max (pos, 0)
                pos = min (pos, entry_count)
                return pos

            lsize = settings.lessons.lesson
            wsize = settings.lessons.window * lsize

            new_start = 0

            while True:

                new_end = new_start + lsize

                prev_start = new_start - lsize
                prev_end = prev_start + lsize

                window_start = prev_start - wsize
                window_end = window_start + wsize


                if window_start >= entry_count:
                    break

                start = fit_in_frame (new_start)
                end = fit_in_frame (new_end)
                new = interval (start, end - start)

                start = fit_in_frame (prev_start)
                end = fit_in_frame (prev_end)
                prev = interval (start, end - start)

                start = fit_in_frame (window_start)
                end = fit_in_frame (window_end)
                window = interval (start, end - start)

                self.stateL.append (FloatingWindow.state (new, prev, window))


                new_start += lsize


            self.lesson_cnt = entry_count//lsize
            if entry_count % lsize > 0:
                self.lesson_cnt += 1


            if suggested_index > len (self.stateL):
                self.cur = 0
            else:
                self.cur = suggested_index
    """

    def __init__ (self,settings, entry_count, suggested_index):

            self.entry_count = entry_count

            if entry_count == 0:
                self. total_steps = 0
                self. new_lesson_cnt = 0
                self. new = None
                self. prev = None
                self. window = None
                self. cur = 0

                return


            def fit_in_frame (pos):
                pos = max (pos, 0)
                pos = min (pos, entry_count)
                return pos

            wlcnt = settings.lessons.window
            lsize = settings.lessons.lesson
            wsize = wlcnt * lsize



            self.new_lesson_cnt = entry_count//lsize
            if entry_count % lsize > 0:
                self.new_lesson_cnt += 1


            self.total_steps = 0
            while True:
                wstart = fit_in_frame (self.total_steps * lsize - lsize - wsize)

                if wstart == entry_count:
                    break

                self.total_steps += 1


            if suggested_index > self.total_steps:
                self.cur = 0
            else:
                self.cur = suggested_index

            nstart = self.cur * lsize
            nend = nstart + lsize
            prev_start = nstart - lsize
            wstart = prev_start - wsize

            nstart = fit_in_frame (nstart)
            nend = fit_in_frame (nend)
            prev_start = fit_in_frame (prev_start)
            wstart = fit_in_frame (wstart)

            self.new = interval (nstart, nend - nstart)
            self.prev = interval (prev_start, nstart - prev_start)
            self.window = interval (wstart, prev_start - wstart)





    def is_at_end (self):
        return self.cur == self.total_steps

    def is_at_start (self):
        return self.cur == 0

    def get_cur_new (self):
        return self.new

    def get_cur_prev (self):
        return self.prev

    def get_cur_window (self):
        return self.window

    def get_older (self):
        return interval (0, max (self.entry_count - (self.prev.size + self.new.size + self.window.size), 0))

    def get_lesson_cnt (self):
        return self.new_lesson_cnt

    def get_total_step_cnt (self):
        return self.total_steps

    def is_there_new (self):
        return self.new.size > 0

    def is_there_prev (self):
        return self.prev.size > 0

    def is_there_window (self):
        return self.window.size > 0
