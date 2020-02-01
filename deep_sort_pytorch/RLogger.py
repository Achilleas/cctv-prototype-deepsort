import json

class RLogger():
    """
    Class responsible for logging any events to Redis
    """
    def __init__(self, r=None, host=None, port=None, charset="utf-8", db=0, decode_responses=True, password=''):
        if r != None:
            self.r = r
        elif host != None and port != None:
            self.r = redis.StrictRedis(host=host, port=port, db=db, charset=charset, decode_responses=decode_responses, password=password)
        else:
            raise ValueError('Invalid arguments for redis logger...')

    def record_timestamp_event(self, event, id=None, pipe = None):
        """
        Records the timestamp event to Redis

        Args:
            timestamp_event (dict): must contain keys: (timestamp,
                                        class, **args)
            pipe            (bool): pass pipeline if buffering more commands
                                        to server
        """
        #if 'timestamp' not in timestamp_event:
            #timestamp_event['timestamp'] = get_millis()

        no_pipe = (pipe is None)
        id = str(self.r.incr('event:id'))
        event['id'] = id

        if no_pipe:
            pipe = self.r.pipeline(transaction=True)

        pipe.hmset('events:{}'.format(id), event)  #All event info with key as its id
        ref = {id: event['time_start']}
        #print('REF', ref)

        #Time interval events
        pipe.zadd('events', ref) #event ids scored by timestamp
        pipe.zadd('events:{}'.format(event['class_id']), ref) #class specific event ids
        pipe.zadd('events_vid', {(id + '_' + str(event['video_id'])) : event['time_start']})

        pipe.sadd('event:types', event['class_id']) #Store set of event types

        #print('done?')
        if no_pipe:
            pipe.execute()

        return id

    def record_tracked_object(self, video_id, time_start, time_end, rectangle_l, class_id):
        """
        Record parameter information of run
        Args:
            run_id (str) :
        """
        event = {'video_id' : video_id,
                'time_start' : time_start,
                'time_end' : time_end,
                'rectangle_l' : json.dumps(rectangle_l),
                'class_id' : class_id}

        #print('RECORDING EVENT:', event)
        for k in event.keys():
            print(k, type(event[k]))
        redis_id = self.record_timestamp_event(event)
        return redis_id

    def record_video_size(self, video_id, size, pipe=None):
        no_pipe = (pipe is None)

        if no_pipe:
            pipe = self.r.pipeline(transaction=True)

        pipe.set('cctv_{}-shape_x'.format(video_id), size[0])
        pipe.set('cctv_{}-shape_y'.format(video_id), size[1])
        pipe.set('cctv_{}-channels'.format(video_id), size[2])

        if no_pipe:
            pipe.execute()

    def get_video_size(self, video_id, pipe=None):
        no_pipe = (pipe is None)

        if no_pipe:
            pipe = self.r.pipeline(transaction=True)

        pipe.get('cctv_{}-shape_x'.format(video_id))
        pipe.get('cctv_{}-shape_y'.format(video_id))
        pipe.get('cctv_{}-channels'.format(video_id))

        if no_pipe:
            s = pipe.execute()
        return [int(s_v) for s_v in s]

    def update_tracked_object(self, redis_id, update_d, pipe=None):
        no_pipe = (pipe is None)
        if no_pipe:
            pipe = self.r.pipeline(transaction=True)

        event_d = self.r.hgetall('events:{}'.format(redis_id))
        #print(update_d)
        #print('BEFOREEE', self.r.hgetall('events:{}'.format(redis_id)))
        for key in update_d.keys():
            if key == 'rectangle_l':
                event_d['rectangle_l'] = json.dumps(update_d['rectangle_l'])
            else:
                event_d[key] = update_d[key]
        pipe.hmset('events:{}'.format(redis_id), event_d)
        if no_pipe:
            pipe.execute()
        #print('AFTER', self.r.hgetall('events:{}'.format(redis_id)))

    def get_interval_events(self, start, end, class_id=None, video_id=None):
        """
        Return event ids taking place between start and end
        Args:
            start      (int): the start timestamp
            end        (int): the end timestamp
            class_id   (str): filter on specific class_id
        Returns:
            event_ids       : list of event ids that fit the criteria
        """
        print('HELOO ASDFJOISDA' , start, end, class_id, video_id)
        if class_id == None:
            event_ids =  self.r.zrangebyscore('events', start, end)
        else:
            event_ids = self.r.zrangebyscore('events:{}'.format(class_id), start, end)

        print(start, end)
        if video_id != None:
            id_video_pairs_str = self.r.zrangebyscore('events_vid', start, end)
            event_ids_vid = [id_video_pair_str.split('_')[0] for id_video_pair_str in id_video_pairs_str if int(id_video_pair_str.split('_')[1]) == int(video_id)]
            event_ids = list(set(event_ids) & set(event_ids_vid))
        return event_ids

    #Given start, end, class ids and video ids
    #  1) return event details
    def get_class_events(self, class_id_l):
        events_l = []

        for class_id in class_id_l:
            events_l.extend(self.r.zrange('events:{}'.format(class_id), 0, -1))

        return events_l

    def get_video_id_events(self, video_id_l):
        events_l = []

        for video_id in video_id_l:
            id_video_pairs_str = self.r.zrange('events_vid', 0, -1)
            event_ids_vid = [id_video_pair_str.split('_')[0] for id_video_pair_str in id_video_pairs_str]
            events_l.extend(event_ids_vid)
        return events_l

    def get_event_details(self, event_ids, pipe=None):
        print(event_ids)
        no_pipe = (pipe is None)

        if no_pipe:
            pipe = self.r.pipeline(transaction=True)

        for event_id in event_ids:
            pipe.hgetall('events:{}'.format(event_id))

        if no_pipe:
            result = pipe.execute()

        print(result)
