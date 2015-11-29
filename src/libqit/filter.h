#ifndef QIT_FILTER_H

#include <stdlib.h>

namespace qit {

template<typename T, typename F> class FilterIterator {
	public:
		typedef typename T::value_type value_type;
		FilterIterator(const T &iterator, const F &functor) : iterator(iterator) {}

		bool next(value_type &out) {
		    typename T::value_type v;
			while (iterator.next(v))
            {
                if (functor(v))
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

        QIT_ITERATOR_WRITE_METHOD

	protected:
		T iterator;
        F functor;
};

}

#endif // QIT_FILTER_H
