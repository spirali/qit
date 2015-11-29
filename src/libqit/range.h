#ifndef QIT_RANGE_H

#include <stdlib.h>
#include <stdio.h>

namespace qit {

class RangeIterator {
    public:
	typedef int value_type;
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

    protected:
    value_type start;
	value_type end;
	value_type step;
	value_type value;
};

class RangeGenerator {
    public:
	typedef int value_type;
	RangeGenerator(value_type start, value_type end)
	    : start(start), end(end) {}

	void generate(value_type &out) {
	    out = (rand() % (end - start)) + start;
	}

    protected:
    value_type start;
	value_type end;
};

template<typename T> void write(FILE *out, T value)
{
    value.write(out);
}

template<> void write<int>(FILE *out, int value)
{
    fwrite(&value, sizeof(int), 1, out);
}
}

#endif // QIT_RANGE_H
