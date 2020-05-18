import logging

import psycopg2
import logging

from config import DATABASES

logger = logging.getLogger(__name__)



class SQLHelper(object):

    def __init__(self):
        try:

            logger.info('SQLHelper.__iniit__() invoked.')

            self.connection_str = 'host=' + DATABASES['default']['HOST'] + ' dbname=' + DATABASES['default'][
                'NAME'] + ' user=' + DATABASES['default']['USER'] + ' password=' + DATABASES['default'][
                                      'PASSWORD'] + ' port=' + DATABASES['default']['PORT']
            self.connection = psycopg2.connect(self.connection_str)
            self.cursor = self.connection.cursor()

            logger.info('SQLHelper.__iniit__() end.')
        except Exception as ex:
            logger.error('Exception in SQLHelper.__init__(): %s', ex)
            raise ex

    def retrieve_data(self, sql, param=None):
        try:

            if self.connection is None or self.connection.closed:
                self.__init__()

            if param is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, param)

            columns = [column[0] for column in self.cursor.description]

            data = []
            for row in self.cursor.fetchall():
                data.append(dict(zip(columns, row)))

            result = {'data': data, 'columns': columns}

            return result

        except Exception as ex:
            logger.error('Exception in SQLHelper.retreive_data(): %s', ex)
            raise ex
        finally:
            self.__close_connection()

    def crud_operation(self, sql, param=None):
        try:

            logger.info('SQLHelper.crud_operation() invoked.')

            if self.connection is None or self.connection.closed:
                self.__init__()

            if param is None:
                self.cursor.execute(sql)
            else:
                # logger.info('Parameters: %s', param)
                self.cursor.execute(sql, param)

            self.connection.commit()

            data = []

            if self.cursor.description is not None:
                columns = [column[0] for column in self.cursor.description]

                for row in self.cursor.fetchall():
                    data.append(dict(zip(columns, row)))

            result = data

            logger.info('SQLHelper.crud_operation() end.')

            return result

        except Exception as ex:
            self.connection.rollback()
            logger.error('Exception in SQLHelper.crud_operation(): %s', ex)
            raise ex
        finally:
            self.__close_connection()

    def execute_procedure(self, sql, param):
        try:

            logger.info('SQLHelper.execute_procedure() invoked.')

            if self.connection is None or self.connection.closed:
                self.__init__()

            # result = self.cursor.callproc(sql, param)
            # logger.info('Parameters: %s', param)
            self.cursor.callproc(sql, param)

            self.connection.commit()

            columns = [column[0] for column in self.cursor.description]

            data = []
            for row in self.cursor.fetchall():
                data.append(dict(zip(columns, row)))

            result = {'data': data, 'columns': columns}

            logger.info('SQLHelper.execute_procedure() end.')

            return result

        except Exception as ex:
            logger.error('Exception in SQLHelper.execute_procedure(): %s', ex)
            raise ex
        finally:
            self.__close_connection()

    def __close_connection(self):
        self.cursor.close()
        self.connection.close()
