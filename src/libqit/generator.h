#ifndef QIT_GENERATOR_H

#include <stdlib.h>

namespace qit {

template <typename T> class GeneratorIterator {
	public:
		typedef typename T::value_type value_type;
		GeneratorIterator(T &generator) 
			: generator(generator) {}

		bool next(value_type &out) {
			generator.generate(out);		
			return true;
		}

		void reset() {
		}

	protected:
		T &generator;
};

}

#endif // QIT_RANGE_H
