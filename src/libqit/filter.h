#ifndef QIT_FILTER_H

#include <stdlib.h>

namespace qit {

template<typename T, typename F> class FilterIterator {
	public:
		typedef typename T::value_type value_type;
		FilterIterator(T &iterator) : iterator(iterator) {}

		bool next(value_type &out) {
		    typename T::value_type v;
		    F f;

			while (iterator.next(v))
            {
                if (f(v))
                {
                    out = v;
                    return true;
                }
            }

			return false;
		}

		void reset() {
			iterator.reset();
		}
	protected:
		T &iterator;
};

}

#endif // QIT_FILTER_H
