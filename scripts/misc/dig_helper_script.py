# -*- coding: utf-8 -*-
#100, 20, 4

from DaqBufferExample import main
for i in range(1, 1000):
    main([300, 20, i])
    if i % 50 == 0:
        print 'Done + ' + str(i)