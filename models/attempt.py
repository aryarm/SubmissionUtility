import datetime

class Attempt():
    def __init__(self, attempt_id, start_time, due, step_id, status):
        self.id = attempt_id
        if isinstance(start_time, str):
            start_time = datetime.datetime.fromisoformat(start_time)
        self.start_time = start_time
        if isinstance(due, str):
            due = datetime.datetime.fromisoformat(due)
        self.due = due
        self.step_id = step_id
        self.status = status

    def __str__(self):
        attempt = "attempt: {}\tstep: {}\t".format(self.id, self.step_id)
        time_left = self.due - datetime.datetime.now()
        if time_left.seconds <= 0:
            return attempt+"status: PAST DUE"
        mins = (time_left.seconds//60)%60
        secs = time_left.seconds - 60*mins
        return attempt+"status: {}\t{} mins, {} secs left".format(self.status, mins, secs)

    def __repr__(self):
        return str(self)

    def json(self):
        attempt = vars(self).copy()
        attempt['start_time'] = str(attempt['start_time'])
        attempt['due'] = str(attempt['due'])
        return attempt
