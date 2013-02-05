#!/usr/bin/env python2
#
#
#

import os
import sys
import fdb
import logging
import atexit

def init_logger() :
    """initialize the logger"""
#
# readability over everything else !
# http://www.python.org/dev/peps/pep-0008/#pet-peeves <- Really ? 
# I'm an Object Pascal developer, and that's how we do things, 
# even our editors/ide support this :P
#
    logger = logging.getLogger('convert_quotes')

    # place output to file
    handler   = logging.FileHandler('log/convert.log')
    formatter = logging.Formatter(('[%(asctime)s - %(levelname)s] '
                                   '%(message)s'))

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # place output to screen
    ch        = logging.StreamHandler()
    ch_format = logging.Formatter('%(levelname)s %(message)s')

    ch.setFormatter(ch_format)
    logger.addHandler(ch)

    logger.setLevel(logging.DEBUG)

    return logger



LOGGER = init_logger()
LOGGER.info('Entering convert_quotes.py')
QUOTES_FILE = 'quotes.txt'
SEPARATOR   = '----'
AUTHOR_MARK = '    '



def init_db(logger = LOGGER) :
    """initialize the database connection
       raised an fdb.DatabaseError if database error"""

    try :
        con = fdb.connect(
                           dsn      = '127.0.0.1:quotes',
                           user     = 'sysdba', 
                           password = 'masterkey'
                         )

        logger.info('Connected to the database')

    except fdb.DatabaseError as e :
        logger.critical('Database connection error: %s', e)
        raise e

    return con

def finalize(db_connection, logger=LOGGER) :
    """close the database connection"""

    if not db_connection.closed :
        logger.info('Closing database connection')
        db_connection.close

    else :
        logger.error('The database connection is already closed')


def iter_quotes(quotes_file = QUOTES_FILE, logger = LOGGER) :
    "Walks over the quotes file, yields (quote, author) tuples for each quote"

    with open(quotes_file) as f:
        quote = []

        for line in f:
            if line.rstrip() != SEPARATOR : # not end of quote
                quote.append(line)

            else : # end of quote
                if not quote : # quote is empty ?
                    continue

                # try to extract the author if exists 
                if quote[-1].startswith(AUTHOR_MARK) :
                    author = quote.pop().strip()

                else : # mark it as none it was not found
                    author = None
                
                str_quote = ''.join(quote).rstrip()

                if author :
                    logger.debug('About to work on quote "%s" by "%s"',
                                 str_quote, author
                                )

                else :
                    logger.debug('About to work on quote "%s" with no author',
                                 str_quote
                                )

                # extract it for an external handler
                yield str_quote, author
                quote = []

def insert_author(con, cursor, author, logger=LOGGER) :
    """insert the author to the database"""
    try :
        logger.debug('About to insert author (%s) into the db', author)
        cursor.execute('insert into quote_authors(AUTHOR) values(?)', 
                       (author,))

    except fdb.DatabaseError as e : 
        # usually means that the author already exists in the db ...
        logger.info('Could not insert author (%s): %s', author, e)
        return False

    return True

def find_author_id(con, cursor, author, loggger=LOGGER) :
    """Locate the author ID and return it"""

    author_id = None

    try :
        logger.debug('About to get the author (%s) id', author)

        cursor.execute('select id from quote_authors where author=?', 
                       (author,))

        author_id           = cursor.fetchone()[0]
        logger.debug('Author (%s) id : %d', author, author_id)

    except fdb.DatabaseError as e : # could not get the author id
        logger.info('Could not find author (%s): %s', author, e)
    
    return author_id

def handle_author_db(con, cursor, author, authors_ids, logger=LOGGER) :
    """work on the author side of the quote"""

    author_id = None

    if author :
        if authors_ids.has_key(author) :
            return authors_ids[author]

        logger.debug('Author (%s) does not have a known id', author)
        insert_author(con, cursor, author, logger)

        author_id = find_author_id(con, cursor, author, logger)

        if author_id :
            logger.debug('working with the id for author (%s) : %d', 
                         author, author_id)

            if not authors_ids.has_key(author) :
                logger.debug('Add to authors_ids an new author: %s=%d', 
                             author, author_id) 

                authors_ids[author] = author_id
            else :
                logger.debug('The author (%s) already exist at authors_ids', 
                             author)
        else :
            logger.error('ID is empty, author (%s) was not created ?!', author)
        
    else : # if author
        logger.debug('Author is not set')

    return author_id


def insert_to_db(con, quote, author, authors_ids, logger=LOGGER) :
    """Insert quotes to the database"""

    # open database cursor to make actions such as select and insert
    cursor = con.cursor()

    try :
        author_id = handle_author_db(con, cursor, author,authors_ids, logger)
        if author_id :
            logger.debug('Have author_id of %d', author_id)
        else :
            logger.debug('We do not have author_id')

    except :
        logger.debug('Could not get the author id (due to exception)')
        author_id = None

    try :
        logger.debug('Going to insert quote ("%s") to db', quote)

        cursor.execute(('insert into quotes(body, author_ref) '
                        'values(?, ?)'), (quote, author_id))

        logger.debug('Going to commit everything')

        con.commit()

    except fdb.DatabaseError as e : # could not execute query or commit
        logger.error('Could not insert quote: %s', e)
        con.rollback()

        return False

    return True

def run(con, logger = LOGGER) :
    """The main execution loop"""

    LOGGER.debug('Starting to parse file:')

    counter = 0
    for quote, author in iter_quotes():
        if not insert_to_db(con, quote, author, authors_ids) :
            logger.critical('Could not insert quote ("%s") to database', quote)
            sys.exit(('Could not insert quote ("{0}")' 
                      'to database').format(quote))
        
        counter += 1

    logger.debug('Done parsing file. Total quotes: %d', counter)


if __name__ == '__main__' :
    if not os.path.exists(QUOTES_FILE) :
        LOGGER.critical('The file %s was not found', QUOTES_FILE)
        sys.exit('Error: The file {0} was not found'.format(QUOTES_FILE))

    else :
        LOGGER.debug('Found the quote file')

    LOGGER.debug('Starting the initialization ...')

    con = init_db()
    atexit.register(finalize, con)

    try :
        run(con)

    except :
        LOGGER.critical('Unexpected exception was raised: %s', 
                        sys.exc_info()[0])

        finalize(con)
        sys.exit()

