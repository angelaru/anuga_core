
class Operator:
    """Operator - generic structure for a fractional operator
    
    This is the base class for all fractional step operators
    """ 

    def __init__(self, domain):
        
        self.domain = domain
        self.domain.set_fractional_step_operator(self)

        if domain.numproc > 1:
            msg = 'Not implemented to run in parallel'
            assert self.__parallel_safe(), msg

        self.logging = False
        self.logging_file = ''

    def __call__(self):

        #timestep = self.domain.get_timestep()
        raise Exception('Need to implement __call__ for your operator')
                    
    def get_timestep(self):

        return self.domain.get_timestep()

    def __parallel_safe(self):
        """By default an operator is not parallel safe
        """
        return True

    def statistics(self):

        message = 'You need to implement operator statistics for your operator'
        return message
    

    def print_statistics(self):

        print self.statistics()


    def timestepping_statistics(self):

        message  = 'You need to implement timestepping statistics for your operator'
        return message

    def print_timestepping_statistics(self):

        print self.timestepping_statistics()


    def log_timestepping_statistics(self):

        from anuga.utilities.system_tools import log_to_file
        if self.logging:
            log_to_file(self.log_filename, self.timestepping_statistics())
            