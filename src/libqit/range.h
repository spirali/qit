#ifndef QIT_RANGE_H
#define QIT_RANGE_H

#include <stdlib.h>

namespace qit {

class RangeIterator {
    public:
	typedef int value_type;
	RangeIterator() {}
	RangeIterator(value_type start, value_type end, value_type step)
	    : end(end), start(start), value(start), step(step) {}

	bool next(value_type &out) {
	    if (value >= end) {
		    return false;
	    }
	    out = value;
	    value += step;
	    return true;
	}

	void reset() {
	    value = start;
	}

	QIT_ITERATOR_WRITE_METHOD

    protected:
    value_type start;
	value_type end;
	value_type step;
	value_type value;
};

}

#endif // QIT_RANGE_H
