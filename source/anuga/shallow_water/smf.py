#
# slide_tsunami function
#

"""This function returns a callable object representing an initial water
   displacement generated by a submarine sediment slide.

Using input parameters:

Required
 length  downslope slide length
 depth   water depth to slide centre of mass
 slope   bathymetric slope

Optional
 x0      x origin (0)
 y0      y origin (0)
 alpha   angular orientation of slide in xy plane (0)
 w       slide width (0.25*length)
 T       slide thickness (0.01*length)
 g       acceleration due to gravity (9.8)
 gamma   specific density of sediments (1.85)
 Cm      added mass coefficient (1)
 Cd      drag coefficient (1)
 Cn      friction coefficient (0)
 psi     (0)
 dx      offset of second Gaussian (0.2*width of first Gaussian)
 kappa   multiplier for sech^2 function (3.0)
 kappad  multiplier for second Gaussian function (0.8)
 zsmall  an amount near to zero (0.01)

The following parameters are calculated:

 a0      initial acceleration
 ut      theoretical terminal velocity
 s0      charactistic distance of motion
 t0      characteristic time of motion
 w       initial wavelength of tsunami
 a2D     2D initial amplitude of tsunami
 a3D     3D initial amplitude of tsunami

The returned object is a callable double Gaussian function that represents
the initial water displacement generated by a submarine sediment slide.

Adrian Hitchman
Geoscience Australia, June 2005
"""
def find_min(x0, wa, kappad, dx):
    """Determine eta_min to scale eta(x,y)

       eta(x,y) = n03d/nmin*[-f(y)]*g(x)

       nmin = min (-f(y)*g(x) )
            = -f(ystar)*g(xstar)

       ystar = min (-f(y) ), i.e. diff(-f(y))=0
       xstar = min ( g(x) ), i.e. diff(g(x))=0

       ystar = y0 and -f(ystar)=1.0
    """
    from math import exp, cosh

    step = 0.05
    x = x0+50.
    deriv = 10.0
    count_max = 1000000
    c = 0
    deriv = 10.
    f_ystar = 1.
   
    while c < count_max and deriv > 0:
        deriv = (x-x0)*exp(-((x-x0)/wa)**2.0) - \
                kappad*(x-dx-x0)*exp(-((x-dx-x0)/wa)**2.0)
        
        if deriv <= 0: xstar = x
        x -= step
        c += 1
    
    g_xstar = exp(-((xstar-x0)/wa)**2)-kappad*exp(-((xstar-dx-x0)/wa)**2)

    etastar = g_xstar*f_ystar

    return etastar

def slide_tsunami(length, depth, slope, width=None, thickness=None, \
                  x0=0.0, y0=0.0, alpha=0.0, \
                  gravity=9.8, gamma=1.85, \
                  massco=1, dragco=1, frictionco=0, psi=0, \
                  dx=None, kappa=3.0, kappad=0.8, zsmall=0.01, \
                  scale=None,
                  domain=None, verbose=False):

    from math import sin, tan, radians, pi, sqrt, exp
    
    if domain is not None:
        xllcorner = domain.geo_reference.get_xllcorner()
        yllcorner = domain.geo_reference.get_yllcorner()
        x0 = x0 - xllcorner  # slump origin (relative)
        y0 = y0 - yllcorner
        
    #if width not provided, set to typical value
    if width is None:
        width = 0.25 * length

    #if thickness not provided, set to typical value
    if thickness is None:
        thickness = 0.01 * length

    #calculate some parameters of the slide

    sint = sin(radians(slope))
    tant = tan(radians(slope))
    tanp = tan(radians(psi))

    a0 = gravity * sint * ((gamma-1)/(gamma+massco)) * (1-(tanp/tant))
    ut = sqrt((gravity*depth) * (length*sint/depth) \
                    * (pi*(gamma-1)/(2*dragco)) * (1-(tanp/tant)))
    s0 = ut**2 / a0
    t0 = ut / a0

    #calculate some parameters of the water displacement produced by the slide

    w = t0 * sqrt(gravity*depth)
    a2D = s0 * (0.0574 - (0.0431*sint)) \
             * (thickness/length) \
             * ((length*sint/depth)**1.25) \
             * (1 - exp(-2.2*(gamma-1)))
    a3D = a2D / (1 + (15.5*sqrt(depth/(length*sint))))

    from math import sqrt, log, e
    dx = 2.0 * (w * sqrt(-log((zsmall/a3D),e))) / 5.0
        
    # determine nmin for scaling of eta(x,y)
    nmin = find_min(x0,w,kappad,dx)  
    
    if scale is None:
        scale = a3D/nmin
        
    #a few temporary print statements
    if verbose is True:
        print '\nThe slide ...'
        print '\tLength: ', length
        print '\tDepth: ', depth
        print '\tSlope: ', slope
        print '\tWidth: ', width
        print '\tThickness: ', thickness
        print '\tx0: ', x0
        print '\ty0: ', y0
        print '\tAlpha: ', alpha
        print '\tAcceleration: ', a0
        print '\tTerminal velocity: ', ut
        print '\tChar time: ', t0
        print '\tChar distance: ', s0
        print '\nThe tsunami ...'
        print '\tWavelength: ', w
        print '\t2D amplitude: ', a2D
        print '\t3D amplitude: ', a3D
        print '\tscale for eta(x,y):', scale

    #keep an eye on some of the assumptions built into the maths

    if ((slope < 5) or (slope > 30)):
        if verbose is True:
            print 'WARNING: slope out of range (5 - 30 degrees) ', slope
    if ((depth/length < 0.06) or (depth/length > 1.5)):
        if verbose is True:
            print  'WARNING: d/b out of range (0.06 - 1.5) ', depth/length
    if ((thickness/length < 0.008) or (thickness/length > 0.2)):
        if verbose is True:
            print 'WARNING: T/b out of range (0.008 - 0.2) ', thickness/length
    if ((gamma < 1.46) or (gamma > 2.93)):
        if verbose is True:
            print 'WARNING: gamma out of range (1.46 - 2.93) ', gamma

    return Double_gaussian(a3D, w, width, x0, y0, alpha, kappa, kappad, zsmall, dx, scale)

#
# slump_tsunami function
#

"""This function returns a callable object representing an initial water
   displacement generated by a submarine sediment slump.

Using input parameters:

Required
 length  downslope slump length
 depth   water depth to slump centre of mass
 slope   bathymetric slope

Optional
 x0      x origin (0)
 y0      y origin (0)
 alpha   angular orientation of slide in xy plane (0)
 w       slump width (1.0*length)
 T       slump thickness (0.1*length)
 R       slump radius of curvature (b^2/(8*T))
 del_phi slump angular displacement (0.48)
 g       acceleration due to gravity (9.8)
 gamma   specific density of sediments (1.85)
 Cm      added mass coefficient (1)
 Cd      drag coefficient (1)
 Cn      friction coefficient (0)
 dx      offset of second Gaussian (0.2*width of first Gaussian)
 kappa   multiplier for sech^2 function (3.0)
 kappad  multiplier for second Gaussian function (0.8)
 zsmall  an amount near to zero (0.01)

The following parameters are calculated:

 a0      initial acceleration
 um      maximum velocity
 s0      charactistic distance of motion
 t0      characteristic time of motion
 w       initial wavelength of tsunami
 a2D     2D initial amplitude of tsunami
 a3D     3D initial amplitude of tsunami

The returned object is a callable double Gaussian function that represents
the initial water displacement generated by a submarine sediment slump.

Adrian Hitchman
Geoscience Australia, June 2005
"""

def slump_tsunami(length, depth, slope, width=None, thickness=None, \
                  radius=None, dphi=0.48, x0=0.0, y0=0.0, alpha=0.0, \
                  gravity=9.8, gamma=1.85, \
                  massco=1, dragco=1, frictionco=0, \
                  dx=None, kappa=3.0, kappad=1.0, zsmall=0.01, scale=None, \
                  domain=None,
                  verbose=False):

    from math import sin, radians, sqrt

    if domain is not None:
        xllcorner = domain.geo_reference.get_xllcorner()
        yllcorner = domain.geo_reference.get_yllcorner()
        x0 = x0 - xllcorner  # slump origin (relative)
        y0 = y0 - yllcorner

    #if width not provided, set to typical value
    if width is None:
        width = length

    #if thickness not provided, set to typical value
    if thickness is None:
        thickness = 0.1 * length

    #if radius not provided, set to typical value
    if radius is None:
        radius = length**2 / (8.0 * thickness)

    #calculate some parameters of the slump

    sint = sin(radians(slope))

    s0 = radius * dphi / 2
    t0 = sqrt((radius*(gamma+massco)) / (gravity*(gamma-1)))
    a0 = s0 / t0**2
    um = s0 / t0

    #calculate some parameters of the water displacement produced by the slump

    w = t0 * sqrt(gravity*depth)
    a2D = s0 * (0.131/sint) \
             * (thickness/length) \
             * (length*sint/depth)**1.25 \
             * (length/radius)**0.63 * dphi**0.39 \
             * (1.47 - (0.35*(gamma-1))) * (gamma-1)
    a3D = a2D / (1 + (2.06*sqrt(depth/length)))

    from math import sqrt, log, e
    dx = 2.0 * (w * sqrt(-log((zsmall/a3D),e))) / 5.0
        
    # determine nmin for scaling of eta(x,y)
    nmin = find_min(x0,w,kappad,dx)  
    
    if scale is None:
        scale = a3D/nmin
        
    #a few temporary print statements
    if verbose is True:
        print '\nThe slump ...'
        print '\tLength: ', length
        print '\tDepth: ', depth
        print '\tSlope: ', slope
        print '\tWidth: ', width
        print '\tThickness: ', thickness
        print '\tRadius: ', radius
        print '\tDphi: ', dphi
        print '\tx0: ', x0
        print '\ty0: ', y0
        print '\tAlpha: ', alpha
        print '\tAcceleration: ', a0
        print '\tMaximum velocity: ', um
        print '\tChar time: ', t0
        print '\tChar distance: ', s0
        print '\nThe tsunami ...'
        print '\tWavelength: ', w
        print '\t2D amplitude: ', a2D
        print '\t3D amplitude: ', a3D
        print '\tDelta x ', dx
        print '\tsmall ', zsmall
        print '\tKappa d ', kappad
        print '\tscale for eta(x,y):', scale

    #keep an eye on some of the assumptions built into the maths

    if ((slope < 10) or (slope > 30)):        
        if verbose is True:
            print 'WARNING: slope out of range (10 - 30 degrees) ', slope
    if ((depth/length < 0.34) or (depth/length > 0.5)):     
        if verbose is True:
            print  'WARNING: d/b out of range (0.34 - 0.5) ', depth/length
    if ((thickness/length < 0.10) or (thickness/length > 0.15)):     
        if verbose is True:
            print 'WARNING: T/b out of range (0.10 - 0.15) ', thickness/length
    if ((radius/length < 1.0) or (radius/length > 2.0)):     
        if verbose is True:
            print 'WARNING: R/b out of range (1 - 2) ', radius/length
    if ((dphi < 0.10) or (dphi > 0.52)):     
        if verbose is True:
            print 'WARNING: del_phi out of range (0.10 - 0.52) ', dphi
    if ((gamma < 1.46) or (gamma > 2.93)):     
        if verbose is True:
            print 'WARNING: gamma out of range (1.46 - 2.93) ', gamma

    return Double_gaussian(a3D, w, width, x0, y0, alpha, kappa, kappad, zsmall, dx, scale)

#
# Double_gaussian class
#

"""This is a callable class representing the initial water displacment 
   generated by a sediment slide or slump.

Using input parameters:

Required
 w       initial wavelength of tsunami
 a3D     3D initial amplitude of tsunami
 width   width of smf

Optional
 x0      x origin of smf
 y0      y origin of smf
 alpha   angular orientation of smf in xy plane (0)
 dx      offset of second Gaussian (0.2*width of first Gaussian)
 kappa   multiplier for sech^2 function (3.0)
 kappad  multiplier for second Gaussian function (0.8)
 zsmall  an amount near to zero (0.01)

Adrian Hitchman
Geoscience Australia, June 2005
"""

class Double_gaussian:

    def __init__(self, a3D, wavelength, width, x0, y0, alpha, \
                 kappa, kappad, zsmall, dx, scale):
        self.a3D = a3D
        self.wavelength = wavelength
        self.width = width
        self.x0 = x0
        self.y0 = y0
        self.alpha = alpha
        self.kappa = kappa
        self.kappad = kappad
        self.scale = scale

        if dx is None:
            from math import sqrt, log, e
            dx = 2.0 * (self.wavelength * sqrt(-log((zsmall/self.a3D),e))) / 5.0
        self.dx = dx

    def __call__(self, x, y):
        """Make Double_gaussian a callable object.

        If called as a function, this object returns z values representing
        the initial 3D distribution of water heights at the points (x,y)
        produced by a submarine mass failure.
        """

        from math import sin, cos, radians, exp, cosh
        from Numeric import zeros, Float

        #ensure vectors x and y have the same length
        N = len(x)
        assert N == len(y)

        am = self.a3D
        am2 = 1.0
        wa = self.wavelength
        wi = self.width
        x0 = self.x0
        y0 = self.y0
        alpha = self.alpha
        dx = self.dx
        kappa = self.kappa
        kappad = self.kappad
        scale = self.scale

        #double Gaussian calculation assumes water displacement is oriented
        #E-W, so, for displacement at some angle alpha clockwise from the E-W
        #direction, rotate (x,y) coordinates anti-clockwise by alpha

        cosa = cos(radians(alpha))
        sina = sin(radians(alpha))

        xr = ((x-x0) * cosa - (y-y0) * sina) + x0
        yr = ((x-x0) * sina + (y-y0) * cosa) + y0

        z = zeros(N, Float)
        maxz = 0.0
        minz = 0.0
        for i in range(N):
            try:
                z[i] =  -scale / ((cosh(kappa*(yr[i]-y0)/(wi+wa)))**2) \
                            * (exp(-((xr[i]-x0)/wa)**2) - \
                                kappad*exp(-((xr[i]-dx-x0)/wa)**2))
                if z[i] > maxz: maxz = z[i]
                if z[i] < minz: minz = z[i]
                
            except OverflowError:
                pass
                
        return z

    def determineDX(self, zsmall):
        """Determine a suitable offset for the second Gaussian function.

        A suitable offset for the second Gaussian function is taken to
        be some fraction of the 'width' of the first Gaussian function.

        The 'width' of the first Gaussian is obtained from the range of
        the x coordinates over which the function takes values from
        'near zero', through 1, and back to 'near zero'.

        The parameter zsmall passed to this function specifies how much
        'near zero' is.
        """

        from math import sqrt, log, e
        
        a = self.a3D
        c = self.wavelength

        self.dx = 2.0 * (c * sqrt(-log((zsmall/a),e))) / 5.0

        return self.dx

