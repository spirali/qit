#ifndef QIT_TAKE_H

#include <stdlib.h>

namespace qit {

template<typename T> class TakeIterator {
	public:
		typedef typename T::value_type value_type;
		TakeIterator(T &iterator, int count) : iterator(iterator), count(count) {}

		bool next(value_type &out) {
			if (count == 0) {
				return false;
			}
			count--;
			return iterator.next(out);
		}

		void reset() {
			iterator.reset();
		}
	protected:
		T &iterator;
		int count;
};

}

#endif // QIT_TAKE_H
