#ifndef QIT_RANGE_H

#include <stdlib.h>

namespace qit {

class RangeIterator {
	public:
		typedef unsigned int value_type;
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
		typedef unsigned int value_type;
		RangeGenerator(value_type stop) 
			: stop(stop) {}

		void generate(value_type &out) {
			out = rand() % stop;
		}

	protected:
		value_type stop;
};

}

#endif // QIT_RANGE_H
