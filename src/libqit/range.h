#ifndef QIT_RANGE_H

#include <stdlib.h>
#include <stdio.h>

namespace qit {

class RangeIterator {
    public:
	typedef int value_type;
	RangeIterator(value_type stop)
	    : stop(stop), value(0) {}

	bool next(value_type &out) {
	    if (value == stop) {
		return false;
	    }
	    out = value++;
	    return true;
	}

	void reset() {
	    value = 0;
	}

    protected:
	value_type stop;
	value_type value;
};

class RangeGenerator {
    public:
	typedef int value_type;
	RangeGenerator(value_type stop)
	    : stop(stop) {}

	void generate(value_type &out) {
	    out = rand() % stop;
	}

    protected:
	value_type stop;
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
