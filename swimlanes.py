MIN_LANE_WIDTH=3
LEFT = '<'
RIGHT = '>'
THRU = '-'


class Grid( object ):
    def __init__( self ):
        self.rows = []
        self.cols = 0

    def start_row( self ):
        self.rows.append( [] ) 

    def add_token( self, token ):
        r = self.rows[-1]
        r.append( token )
        self.cols = max( self.cols, len( r ) )

    def __str__( self ):
        # find col_widthsa
        retval = ''
        col_widths = []
        for c in range( self.cols ):
            col_max = 0
            for r in self.rows:
                try:
                    col_max = max( col_max, len( r[c] ) )
                    #print r[c], len( r[c] )
                except IndexError, no_col:
                    pass
            #print col_max
            col_widths.append( col_max )

        #print col_widths
        for r in self.rows:
            for i, token in enumerate( r ):
                if token == RIGHT:
                    token = "-" * (col_widths[i]-1) + token
                if token == LEFT:
                    token = token + "-" * (col_widths[i]-1)
                if token == THRU:
                    token = "-" * col_widths[i]
                if not token[0].isalpha() and token[0] != '+':
                    # left justify 
                    fmt = "%%-%d.%ds" % ( col_widths[i], col_widths[i] ) 
                else:
                    # right justified
                    fmt = "%%-%d.%ds" % ( col_widths[i], col_widths[i] ) 
                retval +=  fmt % token
                retval += " "
            retval += "\n"
        return retval


class Diagram( object ):
    def __init__( self, name ):
        self.name = name
        self.moments = []
        self.lanes = []

    def get_moment( self, name="" ):
        try:
            m = self.moments[-1]
        except IndexError, no_moments:
            m = Moment(name)
            self.moments.append( m ) 
        return m 

    def start_moment( self, name ):
        m = Moment(name)
        self.moments.append( m ) 
        return m

    def add_transition( self, lane1, name, lane2 ):
        m = self.get_moment()
        m.add_transition( Transition( lane1, name, lane2 ) )
        return m

    def render( self ):
        retval = ''
        retval +=  "=" * len( self.name )
        retval += "\n"
        retval +=  self.name + "\n"
        retval +=  "=" * len( self.name )
        retval += "\n"

        g = Grid()
        g.start_row()

        self.collect_lanes()
        #print self.lanes
        for l in self.lanes:
            g.add_token( l )
            g.add_token( ' ' * MIN_LANE_WIDTH )

        for m in self.moments:
            #print m.name
            g.start_row()
            g.start_row()
            g.add_token( m.name )

            for t in m.transitions:
                l1_index = self.lanes.index( t.lane1 )
                l2_index = self.lanes.index( t.lane2 )

                direction = - cmp( l1_index, l2_index )

                left = min( l1_index, l2_index )
                right = max( l1_index, l2_index )
                distance = right - left


                retval += " " * ( MIN_LANE_WIDTH * left )
                g.start_row()
                for i in range( left * 2 ): # 1 for each lane and transitionlane
                    g.add_token( " " * ( MIN_LANE_WIDTH * 1 ) )#left ) )


                if direction == 0:
                    g.add_token( t.func1 );     
                    #g.add_token(">");
                    g.add_token( "---\\" )

                    g.start_row()
                    g.add_token( " " ); 
                    #g.add_token(" "); 
                    g.add_token( "   |" )

                    g.start_row()
                    g.add_token( t.func2 ); 
                    #g.add_token( "<" );
                    g.add_token( "<--/" ) 
                else:
                    if direction == -1:
                        #print t.func2,
                        #print "<",
                        g.add_token( t.func2 )
                        g.add_token( LEFT )
                    else:
                        #print t.func1,
                        g.add_token( t.func1 )

                    #print "-" * ( distance * MIN_LANE_WIDTH ),
                    for i in range( 2*( distance -1 ) ):
                        g.add_token( THRU )

                    if direction == 1:
                        #print ">",
                        #print t.func2
                        g.add_token( RIGHT )
                        g.add_token( t.func2 )
                    else:
                        #print t.func1
                        g.add_token( t.func1 )

		g.add_token( t.name )
                #print t.name

        
        retval += "\n\n"   
        retval += str( g  ) 
        return retval

    def collect_lanes( self ):
        lanes = []
        for m in self.moments:
            for t in m.transitions:
                l1 = t.lane1
                l2 = t.lane2 
                if l1 not in lanes:
                    lanes.append( l1 )
                if l2 not in lanes:
                    lanes.append( l2 )
        self.lanes = lanes
                    


class Moment( object ):
    def __init__( self, name ):
        self.name = name
        self.transitions = []

    def add_transition( self, t ):
        self.transitions.append( t ) 

class Transition( object ):
    def __init__( self, lane1, name, lane2 ):
        self.lane1 = self._extract_lane( lane1 )
        self.func1 = self._extract_func( lane1 )

        self.name = name
        self.lane2 = self._extract_lane( lane2 )
        self.func2 = self._extract_func( lane2 )

    @staticmethod
    def _extract_lane( lstr ):
        if "." in lstr:
            lstr, func = lstr.split( ".", 2 ) 
        return lstr

    @staticmethod
    def _extract_func( lstr ):
        func = "+"
        if "." in lstr:
            lstr, func = lstr.split( ".", 2 ) 
        return func


    def __str__( self ):
        return u"%s %s %s" % ( self.lane1, self.name, self.lane2 )

    

def test():
    d = Diagram("test")
    d.start_moment( "case1" )
    d.add_transition( "client.submit", "POSTS to", "server.find_user" )
    d.add_transition( "server", "calls",    "backend.lookup_user" )
    d.add_transition( "backend", "returns", "server" ) 
    d.add_transition( "server", "returns", "client" )
    d.add_transition( "client", "sets state", "client.pleased" )

    d.start_moment( "case2" )
    d.add_transition( "client.activate", "calls", "backend.find_or_create" )
    d.add_transition( "backend", "returns to", "client.handle_id" )
    print d.render()

class Frame( object ):
    def __init__( self, obj, depth=0 ):
        self.obj = obj
        self.depth = depth

	if "." in self.obj:
            self.ns, self.func = self.obj.split(".",2) 
        else:
	    self.ns, self.func = obj, obj

    def __str__( self ):
        if "." in self.obj:
            ns,func = self.obj.split(".",2) 
            return "%s:%s.%s" % ( ns, self.depth, func )
        return "%s:%s" % ( self.obj, self.depth )

class LoggerDiagram( Diagram ):
    def __init__( self, name ):
        super( LoggerDiagram, self ).__init__( name )
        self._callstack = []


    def _get_caller( self ):
        if len( self._callstack ):
            return self._callstack[-1]
        else:
            return Frame("ENTRY")


    def _push_caller( self, caller ):
        self._callstack.append( caller )


    def _pop_caller( self ):
        return self._callstack.pop()


    def called_with( self, callee, kwargs ):
        caller_frame = self._get_caller()
        callee_frame = Frame(callee)

        if caller_frame.obj == callee_frame.obj:
            # recursed
            #callee = "~" + callee # to nested stack frame
            callee_frame.depth = caller_frame.depth + 1

        self.add_transition( str(caller_frame),
            ",",#( %s )" % str(kwargs), 
            str(callee_frame)+ "( %s )" % str(kwargs), 
        ) 
        self._push_caller( callee_frame ) # so if we call anyone, they can find us

    def returning( self, kwargs ):
        us = self._pop_caller()
        caller = self._get_caller()
        #self.add_transition( str(us)+ " returning %s" % str( kwargs ), 
        self.add_transition( us.ns +":" +str(us.depth) + ".return %s" % str( kwargs ), 
	    '.',
            str(caller),
        )

    def excepting( self, kwargs ):
        us = self._pop_caller()
        caller = self._get_caller()
        #self.add_transition( str(us)+ " returning %s" % str( kwargs ), 
        self.add_transition( us.ns +":" +str(us.depth) + ".uncaught excption %s" % str( kwargs ), 
	    '.',
            str(caller),
        )


    def dec_maker( self, name ):
        #print "in dec-maker"
        _DL_ = self
        _NAME_ = name
        def wrapper( fn ):
            #print "in wrapper"
            def wrapped( *args, **kwargs ):
                #print "in wrapped"
                params = []
		if args:
			params = args
		if kwargs:
			params.append( kwargs )
                _DL_.called_with( _NAME_, params )
                try:
                    retval = fn( *args, **kwargs )
                    _DL_.returning( retval )
                    return retval
                except Exception, e:
                    _DL_.excepting( e )
                    raise e
            return wrapped
        return wrapper


def test_likely_code_integration():
    d = LoggerDiagram("Test2" )
    d.start_moment( "myentrypoint" )
    d.called_with( "server.index", "a,b,c" )
    
    #/ calls lib.func
    #/ lib.func logs entry and args
    d.called_with( "lib.func1", "a',b', c'" )
    # ...
    d.returning( "r1,r2,r3" )

    #/ back inserver
    d.returning( "s1,s2,s3" )


    d.start_moment( 'recurser' ) 
   
    d.called_with( "lib.rfunc", [1,2] )
    d.called_with( "lib.rfunc", "1" )
    d.called_with( "lib.rfunc", "1" )
    d.called_with( "server.helper",None )
    d.called_with( "dti.subscriber_exists","259298" )
    d.returning( {'task':'success','userID':239298, 'products':['7DPREM', 'DAYPASS']})
    d.returning( {'instance':"h1"})
    d.returning( "r1" )
    d.returning( "r1" )
    d.returning( "r1" )
    print d.render()

def test_decorator():
    d = LoggerDiagram("test3")
    d.start_moment( 'decorator' ) 

    @d.dec_maker("dti.subscriber_info")
    def subscriber_info(userID):
        return {'userID':userID, 'data':[1,2,3] }  

    @d.dec_maker("mylib.myfunc")
    def myfunc( depth ):
        if depth > 0:
            x = myfunc( depth-1 )
        if depth == 2:
            subscriber_info( depth )
        if depth == 3:
            x = 1/0
        return depth

    try:
        myfunc(4)
    except Exception, e:
        pass
    print d.render()

def test_generator():
    d = LoggerDiagram("test4")
    d.start_moment( "generators" )

    @d.dec_maker( "local.mygen")
    def a_generator_says_wat( num ):
        for x in range( num ):
            yield x

    for i in a_generator_says_wat(3):
        print i

    print d.render()


if __name__ == '__main__':
    test()
    test_likely_code_integration()
    test_decorator()
    test_generator()

